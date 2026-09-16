"""
Minimal GeoPackage (.gpkg) feature reader — no GDAL/geopandas dependency.

Reads feature tables directly via sqlite3 (a .gpkg is just a SQLite database)
and decodes the GeoPackageBinary geometry blobs (a small header wrapping
standard ISO WKB) with the stdlib `struct` module. Only Polygon and
MultiPolygon are supported, which is all NUTS boundary layers use.

See OGC GeoPackage spec 2.1.3 ("GeoPackage Binary Header") for the header
layout this decodes.
"""
import sqlite3
import struct


def _read_wkb_geometry(data, offset):
    """Decode one ISO WKB geometry (Point/Polygon/MultiPolygon) starting at
    `offset`. Returns (geojson_geometry_dict, next_offset)."""
    byte_order = "<" if data[offset] == 1 else ">"
    geom_type = struct.unpack_from(byte_order + "I", data, offset + 1)[0]
    pos = offset + 5

    def read_ring():
        nonlocal pos
        num_points = struct.unpack_from(byte_order + "I", data, pos)[0]
        pos += 4
        coords = list(struct.unpack_from(byte_order + f"{num_points * 2}d", data, pos))
        pos += num_points * 2 * 8
        return [[coords[i], coords[i + 1]] for i in range(0, len(coords), 2)]

    def read_polygon_body():
        nonlocal pos
        num_rings = struct.unpack_from(byte_order + "I", data, pos)[0]
        pos += 4
        return [read_ring() for _ in range(num_rings)]

    if geom_type == 3:  # Polygon
        rings = read_polygon_body()
        geom = {"type": "Polygon", "coordinates": rings}
    elif geom_type == 6:  # MultiPolygon
        num_polys = struct.unpack_from(byte_order + "I", data, pos)[0]
        pos += 4
        polygons = []
        for _ in range(num_polys):
            # Each sub-geometry repeats its own byte-order + type header.
            sub_byte_order = "<" if data[pos] == 1 else ">"
            assert sub_byte_order == byte_order, "mixed endianness in MultiPolygon not supported"
            sub_type = struct.unpack_from(byte_order + "I", data, pos + 1)[0]
            assert sub_type == 3, f"expected Polygon (3) inside MultiPolygon, got {sub_type}"
            pos += 5
            polygons.append(read_polygon_body())
        geom = {"type": "MultiPolygon", "coordinates": polygons}
    else:
        raise NotImplementedError(f"WKB geometry type {geom_type} not supported")

    return geom, pos


# Envelope indicator code (bits 1-3 of the flags byte) -> number of doubles it stores.
_ENVELOPE_DOUBLE_COUNT = {0: 0, 1: 4, 2: 6, 3: 6, 4: 8}


def _decode_gpkg_geometry(blob):
    """Strip the GeoPackageBinary header (magic 'GP' + version + flags +
    srs_id + optional envelope) and decode the ISO WKB body that follows."""
    if blob[0:2] != b"GP":
        raise ValueError("not a GeoPackage geometry blob (missing 'GP' magic)")
    flags = blob[3]
    header_byte_order = "<" if (flags & 0x01) else ">"
    envelope_code = (flags >> 1) & 0x07
    num_envelope_doubles = _ENVELOPE_DOUBLE_COUNT[envelope_code]
    # header: magic(2) + version(1) + flags(1) + srs_id(4) + envelope(8*n)
    offset = 2 + 1 + 1 + 4 + 8 * num_envelope_doubles
    geom, _ = _read_wkb_geometry(blob, offset)
    return geom


def read_features(gpkg_path, table, property_columns, where_sql=None, where_params=()):
    """Read a GeoPackage feature table into a list of
    (properties_dict, geojson_geometry_dict) tuples.

    `property_columns` — column names to keep as GeoJSON feature properties.
    `where_sql` / `where_params` — optional SQL WHERE clause (without the
    "WHERE" keyword) and its bound parameters, e.g. where_sql="LEVL_CODE = ?",
    where_params=(3,).
    """
    con = sqlite3.connect(str(gpkg_path))
    try:
        cur = con.cursor()
        cols_sql = ", ".join([f'"{c}"' for c in property_columns] + ['"Shape"'])
        sql = f'SELECT {cols_sql} FROM "{table}"'
        if where_sql:
            sql += f" WHERE {where_sql}"
        cur.execute(sql, where_params)
        results = []
        for row in cur.fetchall():
            props = dict(zip(property_columns, row[:-1]))
            geometry = _decode_gpkg_geometry(row[-1])
            results.append((props, geometry))
        return results
    finally:
        con.close()
