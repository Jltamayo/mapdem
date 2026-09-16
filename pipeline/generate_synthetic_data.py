"""
Generates synthetic indicator values for every NUTS3 region in the GISCO
GeoPackage (data/NUTS_RG_20M_2024_4326.gpkg), so the site (docs/index.html)
can be built and tested end-to-end against the full, real region set before
partner indicator data arrives. Only the indicator values are synthetic —
the geometries and region codes/names are real Eurostat GISCO 2024 data.
Partner data will simply replace this CSV later; the NUTS3 set and the
geometries stay the same.

Output goes straight into docs/data/processed/, because that folder is the
single source of truth GitHub Pages actually serves once the repo is
configured to publish from /docs (see README). There is no separate
"internal" copy — one location, always publishable.

Run:
    python pipeline/generate_synthetic_data.py
"""
import json
import random
from pathlib import Path

import pandas as pd

from gpkg_reader import read_features

random.seed(42)

GPKG_PATH = Path(__file__).resolve().parents[1] / "data" / "NUTS_RG_20M_2024_4326.gpkg"
GPKG_TABLE = "NUTS_RG_20M_2024_4326"

# Each of the 5 top-level indicators ("domains") is itself the combination of
# 3 base sub-indicators — matching JUSTPLACE's own domain descriptions (Task
# 4.1, docs/methodology.md / materials/Proposal-SEP-211195008.pdf p.154), not
# invented labels. Sub-indicator names are illustrative/synthetic (no such
# columns exist yet), but the *structure* — a domain built from several base
# indicators — is real and matches Task 4.1's own framing.
#
# NOTE on method: a domain's value is a simple mean of its sub-indicators,
# each oriented (inverted if needed) to the domain's own direction, skipping
# missing subs and only null if every sub is null. This is deliberately
# simpler than the rank-based method already candidate-implemented in
# analysis/composite_index.R (which treats these same 5 names as the *base*
# indicators of one overall composite, not as 5 domains each with their own
# subs) — the two are not reconciled yet; see PROJECT_MEMORY.md.

# UI language list: the 3 JUSTPLACE working languages (EN/FR/DE) plus one
# local language per Democracy Studios pilot territory identified in the
# proposal — RO (Iasi), NL (Flanders), EL (Karditsa/Volos), SK (Bratislava),
# CA+ES (Barcelona); Hauts-de-France is already covered by FR. The 7th,
# unnamed pilot territory (see CLAUDE.md, "Democracy Studios pilot
# territories") is deliberately not included yet — add it here the same
# way once confirmed, in both this list and every L(...) call below.
LANGUAGES = ["en", "fr", "de", "ro", "nl", "el", "sk", "ca", "es"]


def L(en, fr, de, ro, nl, el, sk, ca, es):
    """Shorthand for a {lang: text} label dict, in the fixed LANGUAGES order
    — keeps the DOMAINS block below readable instead of repeating 9 dict
    keys per string. Translations are machine-quality drafts, not reviewed
    by native speakers — treat as placeholders for this first demo, not
    final deliverable text, especially for ro/nl/el/sk."""
    return {"en": en, "fr": fr, "de": de, "ro": ro, "nl": nl, "el": el, "sk": sk, "ca": ca, "es": es}


DOMAINS = {
    "objective_inequality_index": {
        "direction": "low_is_good",
        "short_label": L("Objective inequality", "Inégalité objective", "Objektive Ungleichheit",
                          "Inegalitate obiectivă", "Objectieve ongelijkheid", "Αντικειμενική ανισότητα",
                          "Objektívna nerovnosť", "Desigualtat objectiva", "Desigualdad objetiva"),
        "label": L(
            "Disparities in access to services, income & inequality",
            "Disparités d'accès aux services, de revenu et d'inégalité",
            "Unterschiede beim Zugang zu Dienstleistungen, Einkommen und Ungleichheit",
            "Disparități în accesul la servicii, venit și inegalitate",
            "Verschillen in toegang tot diensten, inkomen en ongelijkheid",
            "Ανισότητες στην πρόσβαση σε υπηρεσίες, εισόδημα και ανισότητα",
            "Rozdiely v prístupe k službám, príjme a nerovnosti",
            "Disparitats en l'accés a serveis, renda i desigualtat",
            "Disparidades en el acceso a servicios, renta y desigualdad",
        ),
        "subs": {
            "income_gap": ("low_is_good", L(
                "Income inequality (Gini-style gap)", "Inégalité de revenu (écart de type Gini)",
                "Einkommensungleichheit (Gini-ähnliche Lücke)", "Inegalitate a veniturilor (decalaj de tip Gini)",
                "Inkomensongelijkheid (Gini-achtige kloof)", "Εισοδηματική ανισότητα (χάσμα τύπου Gini)",
                "Príjmová nerovnosť (rozdiel typu Gini)",
                "Desigualtat de renda (bretxa tipus Gini)", "Desigualdad de renta (brecha tipo Gini)")),
            "access_to_services": ("high_is_good", L(
                "Access to healthcare/education/transport", "Accès à la santé, à l'éducation et aux transports",
                "Zugang zu Gesundheitsversorgung, Bildung und Verkehr", "Acces la sănătate, educație și transport",
                "Toegang tot zorg, onderwijs en vervoer", "Πρόσβαση σε υγεία, εκπαίδευση και μεταφορές",
                "Prístup k zdravotnej starostlivosti/vzdelávaniu/doprave",
                "Accés a sanitat, educació i transport", "Acceso a sanidad, educación y transporte")),
            "poverty_risk_rate": ("low_is_good", L(
                "Share of population at risk of poverty", "Part de la population exposée au risque de pauvreté",
                "Anteil der von Armut bedrohten Bevölkerung", "Ponderea populației expuse riscului de sărăcie",
                "Aandeel van de bevolking met risico op armoede", "Ποσοστό πληθυσμού σε κίνδυνο φτώχειας",
                "Podiel obyvateľstva ohrozeného chudobou",
                "Percentatge de població en risc de pobresa", "Porcentaje de población en riesgo de pobreza")),
        },
    },
    "perceived_injustice": {
        "direction": "low_is_good",
        "short_label": L("Perceived injustice", "Injustice perçue", "Wahrgenommene Ungerechtigkeit",
                          "Injustiție percepută", "Ervaren onrechtvaardigheid", "Αντιλαμβανόμενη αδικία",
                          "Vnímaná nespravodlivosť", "Injustícia percebuda", "Injusticia percibida"),
        "label": L(
            "Perceived economic injustice & well-being",
            "Injustice économique perçue et bien-être",
            "Wahrgenommene wirtschaftliche Ungerechtigkeit und Wohlbefinden",
            "Injustiție economică percepută și bunăstare",
            "Ervaren economische onrechtvaardigheid en welzijn",
            "Αντιλαμβανόμενη οικονομική αδικία και ευημερία",
            "Vnímaná ekonomická nespravodlivosť a blahobyt",
            "Injustícia econòmica percebuda i benestar",
            "Injusticia económica percibida y bienestar",
        ),
        "subs": {
            "perceived_unfairness": ("low_is_good", L(
                "Share reporting unfair treatment (ESS-style)", "Part déclarant un traitement injuste (type ESS)",
                "Anteil, der unfaire Behandlung angibt (ESS-Stil)",
                "Ponderea celor care raportează un tratament nedrept (stil ESS)",
                "Aandeel dat oneerlijke behandeling meldt (ESS-stijl)",
                "Ποσοστό που αναφέρει άδικη μεταχείριση (τύπου ESS)",
                "Podiel osôb hlásiacich nespravodlivé zaobchádzanie (v štýle ESS)",
                "Percentatge que declara un tracte injust (estil ESS)",
                "Porcentaje que declara un trato injusto (estilo ESS)")),
            "life_satisfaction": ("high_is_good", L(
                "Self-reported life satisfaction", "Satisfaction de vie autodéclarée",
                "Selbstberichtete Lebenszufriedenheit", "Satisfacția față de viață auto-raportată",
                "Zelfgerapporteerde levenstevredenheid", "Αυτοαναφερόμενη ικανοποίηση από τη ζωή",
                "Subjektívna spokojnosť so životom",
                "Satisfacció vital autodeclarada", "Satisfacción vital autodeclarada")),
            "economic_optimism": ("high_is_good", L(
                "Optimism about future economic conditions", "Optimisme quant aux conditions économiques futures",
                "Optimismus hinsichtlich zukünftiger wirtschaftlicher Bedingungen",
                "Optimism privind condițiile economice viitoare",
                "Optimisme over toekomstige economische omstandigheden",
                "Αισιοδοξία για τις μελλοντικές οικονομικές συνθήκες",
                "Optimizmus ohľadom budúcich ekonomických podmienok",
                "Optimisme sobre les condicions econòmiques futures",
                "Optimismo sobre las condiciones económicas futuras")),
        },
    },
    "civic_participation": {
        "direction": "high_is_good",
        "short_label": L("Civic participation", "Participation civique", "Bürgerschaftliche Beteiligung",
                          "Participare civică", "Maatschappelijke participatie", "Πολιτική συμμετοχή",
                          "Občianska participácia", "Participació cívica", "Participación cívica"),
        "label": L(
            "Voting behaviour & civic participation",
            "Comportement électoral et participation civique",
            "Wahlverhalten und bürgerschaftliche Beteiligung",
            "Comportament electoral și participare civică",
            "Stemgedrag en maatschappelijke participatie",
            "Εκλογική συμπεριφορά και πολιτική συμμετοχή",
            "Volebné správanie a občianska participácia",
            "Comportament electoral i participació cívica",
            "Comportamiento electoral y participación cívica",
        ),
        "subs": {
            "voter_turnout": ("high_is_good", L(
                "Voter turnout in the most recent elections", "Taux de participation aux dernières élections",
                "Wahlbeteiligung bei den letzten Wahlen", "Prezența la vot la cele mai recente alegeri",
                "Opkomst bij de meest recente verkiezingen", "Προσέλευση ψηφοφόρων στις πιο πρόσφατες εκλογές",
                "Volebná účasť v posledných voľbách",
                "Participació electoral en les eleccions més recents",
                "Participación electoral en las elecciones más recientes")),
            "protest_activity": ("high_is_good", L(
                "Participation in protests/demonstrations", "Participation à des manifestations/rassemblements",
                "Teilnahme an Protesten/Demonstrationen", "Participare la proteste/manifestații",
                "Deelname aan protesten/demonstraties", "Συμμετοχή σε διαμαρτυρίες/διαδηλώσεις",
                "Účasť na protestoch/demonštráciách",
                "Participació en protestes/manifestacions", "Participación en protestas/manifestaciones")),
            "associational_membership": ("high_is_good", L(
                "Membership in civic/associational orgs", "Adhésion à des organisations civiques/associatives",
                "Mitgliedschaft in zivilgesellschaftlichen Organisationen/Vereinen",
                "Apartenența la organizații civice/asociative",
                "Lidmaatschap van maatschappelijke organisaties/verenigingen",
                "Συμμετοχή σε πολιτικές/κοινωνικές οργανώσεις",
                "Členstvo v občianskych/záujmových organizáciách",
                "Pertinença a organitzacions cíviques/associatives",
                "Pertenencia a organizaciones cívicas/asociativas")),
        },
    },
    "democratic_trust": {
        "direction": "high_is_good",
        "short_label": L("Democratic trust", "Confiance démocratique", "Demokratisches Vertrauen",
                          "Încredere democratică", "Democratisch vertrouwen", "Δημοκρατική εμπιστοσύνη",
                          "Demokratická dôvera", "Confiança democràtica", "Confianza democrática"),
        "label": L(
            "Trust & democratic resilience",
            "Confiance et résilience démocratique",
            "Vertrauen und demokratische Resilienz",
            "Încredere și reziliență democratică",
            "Vertrouwen en democratische veerkracht",
            "Εμπιστοσύνη και δημοκρατική ανθεκτικότητα",
            "Dôvera a demokratická odolnosť",
            "Confiança i resiliència democràtica",
            "Confianza y resiliencia democrática",
        ),
        "subs": {
            "institutional_trust": ("high_is_good", L(
                "Trust in national/local institutions", "Confiance dans les institutions nationales/locales",
                "Vertrauen in nationale/lokale Institutionen", "Încredere în instituțiile naționale/locale",
                "Vertrouwen in nationale/lokale instellingen", "Εμπιστοσύνη στους εθνικούς/τοπικούς θεσμούς",
                "Dôvera v národné/miestne inštitúcie",
                "Confiança en les institucions nacionals/locals", "Confianza en las instituciones nacionales/locales")),
            "political_efficacy": ("high_is_good", L(
                "Sense that one's political voice matters", "Sentiment que sa voix politique compte",
                "Gefühl, dass die eigene politische Stimme zählt",
                "Percepția că vocea politică proprie contează",
                "Gevoel dat de eigen politieke stem ertoe doet",
                "Αίσθηση ότι η πολιτική φωνή του ατόμου μετράει",
                "Pocit, že vlastný politický hlas má význam",
                "Sensació que la pròpia veu política compta",
                "Sensación de que la propia voz política cuenta")),
            "corruption_perception": ("low_is_good", L(
                "Perceived level of corruption", "Niveau perçu de corruption",
                "Wahrgenommenes Korruptionsniveau", "Nivelul perceput de corupție",
                "Ervaren niveau van corruptie", "Αντιλαμβανόμενο επίπεδο διαφθοράς",
                "Vnímaná miera korupcie",
                "Nivell percebut de corrupció", "Nivel percibido de corrupción")),
        },
    },
    "media_access_index": {
        "direction": "high_is_good",
        "short_label": L("Media access", "Accès aux médias", "Medienzugang", "Acces la mass-media",
                          "Media-toegang", "Πρόσβαση στα μέσα ενημέρωσης", "Prístup k médiám",
                          "Accés als mitjans", "Acceso a los medios"),
        "label": L(
            "News deserts / media access",
            "Déserts d'information et accès aux médias",
            "Nachrichtenwüsten / Medienzugang",
            "Deserturi informaționale / acces la mass-media",
            "Nieuwswoestijnen / media-toegang",
            "Ενημερωτικές «έρημοι» / πρόσβαση στα μέσα",
            "Mediálne púšte / prístup k médiám",
            "Deserts informatius / accés als mitjans",
            "Desiertos informativos / acceso a los medios",
        ),
        "subs": {
            "local_media_presence": ("high_is_good", L(
                "Presence of local news outlets", "Présence de médias d'information locaux",
                "Vorhandensein lokaler Nachrichtenmedien", "Prezența mass-mediei locale",
                "Aanwezigheid van lokale nieuwsmedia", "Παρουσία τοπικών μέσων ενημέρωσης",
                "Prítomnosť miestnych spravodajských médií",
                "Presència de mitjans d'informació locals", "Presencia de medios de comunicación locales")),
            "digital_literacy": ("high_is_good", L(
                "Digital literacy / media literacy", "Compétences numériques et médiatiques",
                "Digitale Kompetenz / Medienkompetenz", "Alfabetizare digitală / alfabetizare media",
                "Digitale geletterdheid / mediawijsheid", "Ψηφιακός/μιντιακός αλφαβητισμός",
                "Digitálna gramotnosť / mediálna gramotnosť",
                "Alfabetització digital / mediàtica", "Alfabetización digital / mediática")),
            "internet_coverage": ("high_is_good", L(
                "Broadband/internet coverage", "Couverture haut débit/internet",
                "Breitband-/Internetabdeckung", "Acoperire broadband/internet",
                "Breedband-/internetdekking", "Κάλυψη ευρυζωνικού/διαδικτύου",
                "Pokrytie širokopásmovým internetom",
                "Cobertura de banda ampla/internet", "Cobertura de banda ancha/internet")),
        },
    },
}

OUT_DIR = Path(__file__).resolve().parents[1] / "docs" / "data" / "processed"


def load_all_nuts3_regions(gpkg_path=GPKG_PATH, table=GPKG_TABLE):
    """Every NUTS3 region in the GISCO GeoPackage, as (properties, geometry)
    pairs — read once and reused for both the indicator table and the
    GeoJSON, so the ~1345 geometries aren't decoded twice."""
    return read_features(gpkg_path, table, ["NUTS_ID", "NAME_LATN"], where_sql="LEVL_CODE = 3")


def make_indicator_table(regions):
    """One row per real NUTS3 region: the 3 sub-indicators of each domain
    (each independently ~20% missing, simulating "highly inhomogeneous"
    real-world missingness) plus the domain's own value, computed from
    those subs — not drawn independently. NUTS2 parent is derived from the
    code's standard Eurostat nesting (NUTS3 code's first 4 characters)."""
    rows = []
    for props, _geometry in regions:
        nuts3 = props["NUTS_ID"]
        row = {"nuts2": nuts3[:4], "nuts3": nuts3}
        for domain_key, domain in DOMAINS.items():
            sub_values = {}
            for sub_key in domain["subs"]:
                is_missing = random.random() <= 0.2
                sub_values[sub_key] = None if is_missing else round(random.uniform(0, 100), 1)

            oriented = [
                v if sub_direction == domain["direction"] else (100 - v)
                for sub_key, (sub_direction, _desc) in domain["subs"].items()
                if (v := sub_values[sub_key]) is not None
            ]
            row[domain_key] = round(sum(oriented) / len(oriented), 1) if oriented else None
            row.update(sub_values)
        rows.append(row)
    return pd.DataFrame(rows)


def load_all_nuts_names(gpkg_path=GPKG_PATH, table=GPKG_TABLE):
    """Real region names (NAME_LATN — each region's own local-language Latin-
    script name, e.g. "Deutschland", "Cataluña") for every NUTS level in the
    GeoPackage (0=country, 1, 2, 3), keyed by code. This is static reference
    data independent of indicator values — generated once from GISCO, it
    doesn't need to change when indicators are swapped for real partner
    data."""
    rows = read_features(gpkg_path, table, ["NUTS_ID", "NAME_LATN"])
    # A few GISCO rows (e.g. North Macedonia) carry stray leading/trailing
    # whitespace in NAME_LATN itself — strip it rather than pass it through.
    return {props["NUTS_ID"]: props["NAME_LATN"].strip() for props, _geometry in rows}


def build_domain_hierarchy():
    """The DOMAINS structure (labels, directions, sub-indicators) as plain
    JSON, so docs/index.html reads the tab/drill-down hierarchy from one
    file instead of a second hand-kept copy in JS that could drift from
    this one."""
    return {
        domain_key: {
            "direction": domain["direction"],
            "short_label": domain["short_label"],
            "label": domain["label"],
            "subs": {
                sub_key: {"direction": sub_direction, "label": sub_label}
                for sub_key, (sub_direction, sub_label) in domain["subs"].items()
            },
        }
        for domain_key, domain in DOMAINS.items()
    }


def build_geojson(regions):
    """FeatureCollection from the same (properties, geometry) pairs used for
    the indicator table, so every indicator row has a matching boundary and
    vice versa."""
    features = [
        {
            "type": "Feature",
            "properties": {"nuts3": props["NUTS_ID"], "name": props["NAME_LATN"]},
            "geometry": geometry,
        }
        for props, geometry in regions
    ]
    return {"type": "FeatureCollection", "features": features}


if __name__ == "__main__":
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    regions = load_all_nuts3_regions()

    df = make_indicator_table(regions)
    indicators_path = OUT_DIR / "synthetic_indicators.csv"
    df.to_csv(indicators_path, index=False)
    print(f"Wrote {indicators_path} ({len(df)} rows)")

    geo = build_geojson(regions)
    geo_path = OUT_DIR / "synthetic_regions.geojson"
    with open(geo_path, "w", encoding="utf-8") as f:
        json.dump(geo, f, indent=2, ensure_ascii=False)
    print(f"Wrote {geo_path} ({len(geo['features'])} features, real NUTS3 boundaries)")

    names = load_all_nuts_names()
    names_path = OUT_DIR / "nuts_names.json"
    with open(names_path, "w", encoding="utf-8") as f:
        json.dump(names, f, indent=2, ensure_ascii=False, sort_keys=True)
    print(f"Wrote {names_path} ({len(names)} region names, all NUTS levels 0-3)")

    hierarchy = build_domain_hierarchy()
    hierarchy_path = OUT_DIR / "domain_hierarchy.json"
    with open(hierarchy_path, "w", encoding="utf-8") as f:
        json.dump(hierarchy, f, indent=2, ensure_ascii=False)
    print(f"Wrote {hierarchy_path} ({len(hierarchy)} domains)")
