"""Maps F1 ticket store section names to our database section names.

When displaying ticket links, we should show the F1 store name alongside
our name so users can find the right section on the ticket site.

Compiled from auditing tickets.formula1.com section names against our
seed data (seat_sections_data_v2.py) and GP portal sites (silverstone.co.uk,
belgium.gp, singaporegp.sg, etc.) as of March 2026.

Key findings:
- The F1 ticket store (tickets.formula1.com) often uses shorter or slightly
  different names compared to GP portal sites and our database.
- Our database names generally follow the GP portal convention (more
  descriptive, with location context in parentheses).
- The F1 store typically drops parenthetical location hints and uses
  colon-separated tier prefixes (e.g. "Gold 1: Pit Grandstand").

Usage:
    from app.seed.section_name_aliases import F1_STORE_ALIASES

    store_name = F1_STORE_ALIASES.get(circuit_name, {}).get(our_section_name)
    if store_name:
        # Show: "Gold 1: Pit Grandstand" on tickets.formula1.com
        pass
"""

# {circuit_name: {our_db_section_name: f1_ticket_store_name}}
F1_STORE_ALIASES: dict[str, dict[str, str]] = {
    # =========================================================================
    # 1. Albert Park Circuit (Melbourne, Australia)
    # F1 store: tickets.formula1.com/en/f1-3159-australia
    # GP portal: grandprix.com.au
    # Notes: The F1 store sells Australia tickets but grandstand names
    #   (Piastri, Fangio, Brabham, etc.) are set by the local promoter
    #   and appear the same on both platforms. The F1 store lists a
    #   "Fangio Lounge" hospitality option separately.
    # =========================================================================
    "Albert Park Circuit": {
        # Names match between F1 store and our DB; no aliases needed.
        # The F1 store uses the same legend-named grandstand convention.
    },
    # =========================================================================
    # 2. Shanghai International Circuit (China)
    # F1 store: tickets.formula1.com/en/f1-3182-china
    # Notes: F1 store uses "Grandstand H", "Grandstand K" etc. Our DB
    #   adds tier suffixes like "Platinum", "High Gold", "Low Silver".
    # =========================================================================
    "Shanghai International Circuit": {
        "Grandstand A - Platinum": "Grandstand A (Platinum)",
        "Grandstand A - High Gold": "Grandstand A (High Gold)",
        "Grandstand A - Low Silver": "Grandstand A (Low Silver)",
        "Grandstand B (Turn 1)": "Grandstand B",
        "Grandstand H (Turn 14 Hairpin)": "Grandstand H",
        "Grandstand K (Turn 14)": "Grandstand K",
    },
    # =========================================================================
    # 3. Suzuka International Racing Course (Japan)
    # F1 store: tickets.formula1.com/en/f1-3309-japan
    # Notes: F1 store uses simpler names like "Grandstand B2", "Grandstand R",
    #   "Grandstand Q1", "Stand H", "130R / Overpass".
    #   Our DB uses the local seat-naming convention (V2 Seat, A1 Seat, etc.)
    #   with parenthetical descriptions.
    # =========================================================================
    "Suzuka International Racing Course": {
        "V2 Seat (Grandstand Upper Tier)": "Grandstand V2",
        "V1 Seat (Grandstand Lower Tier)": "Grandstand V1",
        "A2 Seat (Main Straight End)": "Grandstand A2",
        "A1 Seat (Main Straight)": "Grandstand A1",
        "B2 Seat (Turn 2 Premium)": "Grandstand B2",
        "B1 Seat (Turn 2)": "Grandstand B1",
        "Q2 Seat (Astemo Chicane)": "Grandstand Q2",
        "R Seat (Final Corner)": "Grandstand R",
        "Q1 Seat (Astemo Chicane Entrance)": "Grandstand Q1",
        "I Seat (Hairpin)": "Grandstand I",
        "C Seat (S-Curves Fan Seat)": "Grandstand C",
        "H Seat (110R Overpass)": "Stand H",
        "E Seat (NIPPO Corner / Dunlop)": "Grandstand E",
        "D Seat (S-Curves / Reverse Bank)": "Grandstand D",
        "M Seat (Spoon Curve)": "Grandstand M",
        "P Seat (Astemo Chicane Entrance)": "Grandstand P",
        "O Seat (West Straight)": "Grandstand O",
        "G Seat (130R / Overpass)": "130R / Overpass",
        "General Admission - West Area": "Spoon Corner Roving (G-J-L-M-N-O)",
    },
    # =========================================================================
    # 4. Miami International Autodrome (USA)
    # F1 store: tickets.formula1.com/en/f1-54987-miami
    # Notes: F1 store uses names like "Turn 1 North Grandstand",
    #   "Start/Finish Grandstand", "North Beach Grandstand",
    #   "Marina Central Grandstand".
    # =========================================================================
    "Miami International Autodrome": {
        "Turn 1 Grandstand (Covered)": "Turn 1 North Grandstand (Covered)",
        "Turn 1 Grandstand (Uncovered)": "Turn 1 North Grandstand",
        "Start and Finish Grandstand (Covered)": "Start/Finish Grandstand (Covered)",
        "Start and Finish Grandstand (Uncovered)": "Start/Finish Grandstand",
        "North Beach Grandstand": "North Beach Grandstand",
        "South Beach Grandstand (Covered)": "South Beach Grandstand",
        "Marina Grandstand": "Marina Central Grandstand",
        "Turn 18 Grandstand": "Turn 18 Grandstand",
        "General Admission - Campus Pass": "General Admission - Campus",
    },
    # =========================================================================
    # 5. Circuit Gilles Villeneuve (Montreal, Canada)
    # F1 store: tickets.formula1.com/en/f1-3215-canada
    # Notes: F1 store uses "Grandstand 31", "Lance Stroll Grandstand",
    #   "Platine Grandstand", "Grandstand Family" (for 33).
    #   Our DB adds parenthetical location descriptors.
    # =========================================================================
    "Circuit Gilles Villeneuve": {
        "Grandstand 1 (Main Straight)": "Grandstand 1",
        "Grandstand Platine (Turn 1)": "Platine Grandstand",
        "Grandstand 11": "Grandstand 11",
        "Grandstand 12 (Turns 1-2-3)": "Grandstand 12",
        "Grandstand 15": "Grandstand 15",
        "Grandstand 21 (Hairpin)": "Grandstand 21",
        "Grandstand 24 (Lance Stroll Grandstand)": "Lance Stroll Grandstand",
        "Grandstand 31 (Back Straight)": "Grandstand 31",
        "Grandstand 33 (Family Grandstand)": "Grandstand Family",
        "General Admission": "General Admission",
    },
    # =========================================================================
    # 6. Circuit de Monaco
    # F1 store: tickets.formula1.com/en/f1-3202-monaco
    # Notes: F1 store uses "Grandstand A1", "Grandstand K", "Grandstand T Upper",
    #   "Grandstand T (covered)", "Le Rocher General Admission", etc.
    #   Our DB adds parenthetical location descriptions.
    # =========================================================================
    "Circuit de Monaco": {
        "Grandstand A1 (Sainte Devote)": "Grandstand A1",
        "Grandstand B (Casino Square)": "Grandstand B",
        "Grandstand C (Portier)": "Grandstand C",
        "Grandstand K1-K2 (Port Hercule)": "Grandstand K",
        "Grandstand K3-K6 (Port Hercule)": "Grandstand K",
        "Grandstand K Gold (Port Hercule Premium)": "Grandstand K Gold Package",
        "Grandstand L (Swimming Pool)": "Grandstand L",
        "Grandstand L Gold (Swimming Pool Premium)": "Grandstand L Gold",
        "Grandstand N (Swimming Pool)": "Grandstand N",
        "Grandstand O (Swimming Pool)": "Grandstand O",
        "Grandstand P (Swimming Pool)": "Grandstand P",
        "Grandstand T (La Rascasse straight)": "Grandstand T (covered)",
        "Grandstand V (La Rascasse)": "Grandstand V",
        "Grandstand V Gold (La Rascasse Premium)": "Grandstand V Gold",
        "Grandstand X1 (Quai Albert 1er)": "Grandstand X1",
        "Grandstand X2 (Quai Albert 1er)": "Grandstand X2",
        "General Admission Z1 (Quai Kennedy)": "General Admission Z1",
        "General Admission Le Rocher": "Le Rocher General Admission",
        "VIP Caravelles Grand Terrace": "VIP Grandstand",
    },
    # =========================================================================
    # 7. Circuit de Barcelona-Catalunya (Spain)
    # F1 store: tickets.formula1.com/en/f1-3190-spain
    # Notes: F1 store uses "Main Grandstand", "Grandstand E", "Grandstand C",
    #   "Grandstand M", "Grandstand T1", "Grandstand V", "Grandstand S",
    #   "General Admission". Our DB adds parenthetical location info.
    # =========================================================================
    "Circuit de Barcelona-Catalunya": {
        "Main Grandstand": "Main Grandstand",
        "Grandstand A": "Grandstand A",
        "Grandstand E (Turn 1)": "Grandstand E",
        "Grandstand H (Stadium Section)": "Grandstand H",
        "Grandstand I": "Grandstand I",
        "Grandstand L (Hillside)": "Grandstand L",
        "Grandstand M": "Grandstand M",
        "Grandstand N (Turn 9)": "Grandstand N",
        "Grandstand S (Chicane)": "Grandstand S",
        "Grandstand F (Turns 2-3)": "Grandstand F",
        "Grandstand G (Turns 3-4)": "Grandstand G",
        "Grandstand T10 (Turn 10)": "Grandstand T10",
        "General Admission": "General Admission",
    },
    # =========================================================================
    # 8. Red Bull Ring (Spielberg, Austria)
    # F1 store: tickets.formula1.com/en/f1-3222-austria
    # Notes: F1 store uses "Start-Finish Grandstand", "Red Bull C-D-E Grandstand",
    #   "T3", "T8 Grandstand", "T9 Grandstand", "T10 Grandstand",
    #   "Steiermark Grandstand", "General Admission".
    #   Our DB has "Schonberg Grandstand" and "3 Corner Gold" which don't
    #   appear directly on the F1 store.
    # =========================================================================
    "Red Bull Ring": {
        "Start-Ziel (Start/Finish Grandstand)": "Start-Finish Grandstand",
        "Red Bull Grandstand": "Red Bull C-D-E Grandstand",
        "T3 Grandstand": "T3",
        "T8 Grandstand": "T8 Grandstand",
        "T9 Grandstand": "T9 Grandstand",
        "Steiermark Grandstand": "Steiermark Grandstand",
        "Schonberg Grandstand": "Schonberg Grandstand",
        "3 Corner Gold": "3 Corner Gold",
        "T10 Grandstand": "T10 Grandstand",
        "General Admission": "General Admission",
    },
    # =========================================================================
    # 9. Silverstone Circuit (Great Britain)
    # F1 store: tickets.formula1.com/en/f1-3226-great-britain
    # GP portal: silverstone.co.uk
    # Notes: F1 store uses names like "Abbey", "Becketts Grandstand",
    #   "Copse Grandstand" (with A suffix in URL), "Village A Grandstand",
    #   "Vale Grandstand", "Chapel Grandstand", "National Pits Straight
    #   Grandstand", "Luffield Grandstand", "Farm Curve", "Stirling A",
    #   "Hamilton Straight B", "Woodcote B", "General Admission",
    #   "T1 Enclosure", "Wellington Enclosure", "Boxpark - The Loop".
    #   Names are very similar; F1 store sometimes appends "Grandstand".
    # =========================================================================
    "Silverstone Circuit": {
        "Abbey A": "Abbey",
        "Abbey B": "Abbey",
        "Becketts": "Becketts Grandstand",
        "Chapel": "Chapel Grandstand",
        "Club A": "Club A",
        "Club Corner": "Club Corner",
        "Copse A": "Copse Grandstand",
        "Copse B": "Copse B",
        "Copse C": "Copse C",
        "Copse D": "Copse D",
        "Farm Curve": "Farm Curve",
        "Hamilton Straight A": "Hamilton Straight A",
        "Hamilton Straight B": "Hamilton Straight B",
        "Landostand": "Landostand",
        "Luffield": "Luffield Grandstand",
        "Luffield Corner": "Luffield Corner",
        "National Pits Straight": "National Pits Straight Grandstand",
        "Stirling A": "Stirling A",
        "Stirling B": "Stirling B",
        "The View": "The View",
        "Vale": "Vale Grandstand",
        "Village A": "Village A Grandstand",
        "Village B": "Village B",
        "Woodcote A": "Woodcote A",
        "Woodcote B": "Woodcote B",
        "Woodcote C": "Woodcote C",
        "General Admission": "General Admission",
    },
    # =========================================================================
    # 10. Circuit de Spa-Francorchamps (Belgium)
    # F1 store: tickets.formula1.com/en/f1-3286-belgium
    # GP portal: belgium.gp, spagrandprix.com
    # Notes: F1 store uses "Gold 1: Pit Grandstand", "Gold 4: Eau Rouge
    #   Grandstand", "Silver 2: Spa Grandstand", "Silver 4: Bruxelles
    #   Grandstand", "Bronze: General Admission", "Grandstand Speed Corner",
    #   "Gold 8: Source Start Grandstand", "Grandstand 17-27", "Combes
    #   Grandstand", "Silver 6", etc.
    # =========================================================================
    "Circuit de Spa-Francorchamps": {
        "Gold 1: Pit": "Gold 1: Pit Grandstand",
        "Gold 2: GP2": "Gold 2: GP2 Grandstand",
        "Gold 3: Eau Rouge": "Gold 3: Eau Rouge Grandstand",
        "Gold 4: Eau Rouge": "Gold 4: Eau Rouge Grandstand",
        "Gold 6: Chicane": "Gold 6: Chicane Grandstand",
        "Gold 7: BIS": "Gold 7: BIS",
        "Gold 8: La Source": "Gold 8: Source Start Grandstand",
        "Gold 9: Pole Position": "Gold 9: Pole Position Grandstand",
        "Silver 1: Francorchamps": "Silver 1: Francorchamps",
        "Silver 2: Spa": "Silver 2: Spa Grandstand",
        "Silver 3: Pouhon": "Silver 3: Pouhon Grandstand",
        "Silver 4: Bruxelles": "Silver 4: Bruxelles Grandstand",
        "Silver 5: Pouhon Exit": "Silver 5: Pouhon Exit",
        "Silver 6: Les Fagnes": "Silver 6",
        "Speed Corner": "Grandstand Speed Corner",
        "Blanchimont 17-27": "Grandstand 17-27",
        "Bronze Area (General Admission)": "Bronze: General Admission",
        "Bronze Area Bruxelles": "Raquette Bronze Comfort Zone",
    },
    # =========================================================================
    # 11. Hungaroring (Hungary)
    # F1 store: tickets.formula1.com/en/f1-3277-hungary
    # Notes: F1 store uses "Hungaroring Grandstand", "Hungaroring Platinium
    #   Grandstand", "Grid 1 Grandstand", "Grid 3", "Podium Grandstand",
    #   "Pit Exit Grandstand", "Red Bull Grandstand", "Apex 2",
    #   "Chicane 3", "Silver 5 Grandstand".
    #   Our DB uses somewhat different names with parenthetical hints.
    # =========================================================================
    "Hungaroring": {
        "Grandstand Hungaroring (Covered)": "Hungaroring Grandstand",
        "Podium Grandstand": "Podium Grandstand",
        "Grandstand T1": "T1 Grandstand",
        "Grandstand Grid 1": "Grid 1 Grandstand",
        "Grandstand Grand Prix 2": "Grand Prix 2 Grandstand",
        "Grandstand Pit Exit 1": "Pit Exit Grandstand",
        "Grandstand Apex 1": "Apex 1 Grandstand",
        "Grandstand Chicane 1": "Chicane 1 Grandstand",
        "Grandstand Fan 2": "Fan 2 Grandstand",
        "General Admission": "General Admission",
    },
    # =========================================================================
    # 12. Circuit Zandvoort (Netherlands)
    # F1 store: tickets.formula1.com/en/f1-42837-netherlands
    # Notes: F1 store uses "Arena Grandstand 1", "Tarzan-In Grandstand 1",
    #   "Eastside Grandstand 3", "Ben Pon Grandstand 2",
    #   "Arena - Out Grandstand", "Eastside Grandstand 2A/2B".
    #   Our DB uses slightly different naming.
    # =========================================================================
    "Circuit Zandvoort": {
        "Main Grandstand": "Ben Pon Grandstand 2",
        "Pit Grandstand": "Pit Grandstand",
        "Tarzan-In 1 (Turn 1)": "Tarzan-In Grandstand 1",
        "Eastside 3 (Banked Turn)": "Eastside Grandstand 3",
        "Arena 1": "Arena Grandstand 1",
        "Ben Pon 2 (Silver)": "Ben Pon Grandstand 2",
        "Hairpin Grandstand": "Arena - Out Grandstand",
        "General Admission": "General Admission",
    },
    # =========================================================================
    # 13. Autodromo Nazionale di Monza (Italy)
    # F1 store: tickets.formula1.com/en/f1-3293-italy
    # Notes: F1 store uses Italian naming with number prefix in parens:
    #   "(6c) Alta Velocita C Grandstand", "(8a) Esterna Prima Variante A",
    #   "(16) Ascari Grandstand", "(22) Parabolica Grandstand",
    #   "(5) Piscina Grandstand", "(21a) Laterale Parabolica A", etc.
    #   Our DB uses "Grandstand N (description)" format.
    # =========================================================================
    "Autodromo Nazionale di Monza": {
        "Grandstand 6 C (Centrale)": "(6c) Alta Velocita C Grandstand",
        "Grandstand 6 B": "(6b) Alta Velocita B Grandstand",
        "Grandstand 4": "(4) Grandstand 4",
        "Grandstand 5 (Piscina)": "(5) Piscina Grandstand",
        "Biassono 7": "(7) Biassono Grandstand",
        "Grandstand 8 A": "(8a) Esterna Prima Variante A Grandstand",
        "Grandstand 8 B": "(8b) Esterna Prima Variante B Grandstand",
        "Grandstand 9": "(9) Seconda Variante Grandstand",
        "Grandstand 14 (Variante Seconda)": "(14) Ascari 2 Bis Grandstand",
        "Grandstand 16 (Ascari)": "(16) Ascari Grandstand",
        "Grandstand 17A (Ascari)": "(15) Ascari Uno Grandstand",
        "Grandstand 18 (Ascari Exit)": "(18) Ascari Exit Grandstand",
        "Grandstand 21 A (Parabolica)": "(21a) Laterale Parabolica A Grandstand",
        "Grandstand 21 B (Parabolica)": "(21b) Laterale Parabolica B Grandstand",
        "Grandstand 22 (Parabolica Entry)": "(22) Parabolica Grandstand",
        "Grandstand 34 (Lesmo)": "(34) Lesmo Grandstand",
        "General Admission (Interno Parabolica)": "Interno Parabolica (General Admission)",
    },
    # =========================================================================
    # 14. Madrid Street Circuit (Spain - from 2026)
    # F1 store: tickets.formula1.com/en/f1-77449-madrid-spain-gp
    # Notes: F1 store uses "G01 Grandstand", "G04 Grandstand",
    #   "G10 Grandstand" etc. with "Seccion" numbering.
    #   This is a brand-new circuit for 2026, names may evolve.
    # =========================================================================
    "Madrid Street Circuit": {
        "Grandstand 1 (Main Grandstand)": "G01 Grandstand",
        "Grandstand 2": "G02 Grandstand",
        "Grandstand 3 (High Speed)": "G03 Grandstand",
        "Grandstand 4 (High Speed)": "G04 Grandstand",
        "Grandstand 5 (High Speed)": "G05 Grandstand",
        "Grandstand 6 (Chicane)": "G06 Grandstand",
        "Grandstand 7 (Chicane)": "G07 Grandstand",
        "Grandstand 8 (Chicane)": "G08 Grandstand",
        "Grandstand 9 (Banking)": "G09 Grandstand",
        "Grandstand 11 (Banking, Covered)": "G11 Grandstand",
        "Grandstand 12 (Banking)": "G10 Grandstand",
        "Grandstand 13 (Esses, Covered)": "G13 Grandstand",
        "Grandstand 14 (Esses)": "G14 Grandstand",
        "Grandstand 15 (Esses)": "G15 Grandstand",
        "Grandstand 16 (Esses)": "G16 Grandstand",
        "General Admission (Pelouse)": "General Admission (Pelouse)",
    },
    # =========================================================================
    # 15. Baku City Circuit (Azerbaijan)
    # F1 store: tickets.formula1.com/en/f1-10851-azerbaijan
    # Notes: F1 store uses "Absheron C Grandstand", "Sahil Grandstand",
    #   "Giz Galasi Grandstand", "Filarmoniya Grandstand",
    #   "Bulvar Grandstand", "Khazar Grandstand", "AzNeft Grandstand",
    #   "Champions Grandstand", "Mugham Grandstand".
    #   Our DB prefixes most names with "Grandstand" which the F1 store
    #   suffixes instead.
    # =========================================================================
    "Baku City Circuit": {
        "Grandstand Absheron C": "Absheron C Grandstand",
        "Grandstand Absheron D": "Absheron D Grandstand",
        "Grandstand Absheron A": "Absheron A Grandstand",
        "Grandstand Absheron B": "Absheron B Grandstand",
        "Grandstand Absheron E": "Absheron E Grandstand",
        "Grandstand Champions": "Champions Grandstand",
        "Grandstand Azneft": "AzNeft Grandstand",
        "Grandstand Icheri Sheher": "Icheri Sheher Grandstand",
        "Grandstand Mugham": "Mugham Grandstand",
        "Grandstand Marine": "Marine Grandstand",
        "Grandstand Khazar": "Khazar Grandstand",
        "Grandstand Bulvar": "Bulvar Grandstand",
        "Grandstand Giz Galasi": "Giz Galasi Grandstand",
        "Grandstand Filarmoniya": "Filarmoniya Grandstand",
        "Grandstand Zafar": "Zafar Grandstand",
    },
    # =========================================================================
    # 16. Marina Bay Street Circuit (Singapore)
    # F1 store: tickets.formula1.com/en/f1-3301-singapore
    # GP portal: singaporegp.sg
    # Notes: F1 store uses "Pit Grandstand", "Super Pit Grandstand",
    #   "Turn 1 Grandstand", "Turn 2 Grandstand", "Chicane @ Turn 2",
    #   "Raffles Grandstand", "Marina Bay Grandstand",
    #   "Premier Walkabout". Names mostly match.
    # =========================================================================
    "Marina Bay Street Circuit": {
        "Super Pit Grandstand": "Super Pit Grandstand",
        "Pit Grandstand": "Pit Grandstand",
        "Turn 1 Grandstand": "Turn 1 Grandstand",
        "Chicane @ Turn 1 Grandstand": "Chicane @ Turn 1",
        "Turn 2 Grandstand": "Turn 2 Grandstand",
        "Chicane @ Turn 2 Grandstand": "Chicane @ Turn 2",
        "Pit Exit Grandstand": "Pit Exit Grandstand",
        "Pit Entry Grandstand": "Pit Entry Grandstand",
        "Marina Bay Grandstand": "Marina Bay Grandstand",
        "Skyline Grandstand": "Skyline Grandstand",
        "Bayfront Grandstand": "Bayfront Grandstand",
        "Promenade Grandstand": "Promenade Grandstand",
        "Raffles Grandstand": "Raffles Grandstand",
        "Republic Grandstand": "Republic Grandstand",
        "Padang Grandstand": "Padang Grandstand",
        "Empress Grandstand": "Empress Grandstand",
        "Connaught Grandstand": "Connaught Grandstand",
        "Stamford Grandstand": "Stamford Grandstand",
        "Orange @ Pit Grandstand": "Orange @ Pit Grandstand",
        "General Admission - Premier Walkabout": "Premier Walkabout",
        "General Admission - Walkabout": "Walkabout",
    },
    # =========================================================================
    # 17. Circuit of the Americas (Austin, USA)
    # F1 store: tickets.formula1.com/en/f1-3320-united-states
    # Notes: F1 store uses "Main Grandstand", "Turn 1 Grandstand",
    #   "Turn 4 Grandstand", "Turn 9 Grandstand", "Turn 12 Grandstand",
    #   "Turn 15 Grandstand", "Turn 19 Grandstand", "General Admission".
    #   Our DB has sub-tiers (Upper/Middle/Lower/Club/Mezzanine/Trackside)
    #   that the F1 store does not differentiate - they sell "Turn 1
    #   Grandstand" as one product.
    # =========================================================================
    "Circuit of the Americas": {
        "Main Grandstand - Club": "Main Grandstand",
        "Main Grandstand - Mezzanine": "Main Grandstand",
        "Main Grandstand - Lower": "Main Grandstand",
        "Main Grandstand - Trackside": "Main Grandstand",
        "Grandstand Turn 1 - Upper": "Turn 1 Grandstand",
        "Grandstand Turn 1 - Middle": "Turn 1 Grandstand",
        "Grandstand Turn 1 - Lower": "Turn 1 Grandstand",
        "Grandstand Turn 4 - Upper": "Turn 4 Grandstand",
        "Grandstand Turn 4 - Lower": "Turn 4 Grandstand",
        "Grandstand Turn 9": "Turn 9 Grandstand",
        "Grandstand Turn 12": "Turn 12 Grandstand",
        "Grandstand Turn 13": "Turn 13 Grandstand",
        "Grandstand Turn 15 - Upper": "Turn 15 Grandstand",
        "Grandstand Turn 15 - Middle": "Turn 15 Grandstand",
        "Grandstand Turn 15 - Lower": "Turn 15 Grandstand",
        "Grandstand Turn 19 - Upper": "Turn 19 Grandstand",
        "Grandstand Turn 19B": "Turn 19B Grandstand",
        "General Admission": "General Admission",
    },
    # =========================================================================
    # 18. Autodromo Hermanos Rodriguez (Mexico City, Mexico)
    # F1 store: tickets.formula1.com/en/f1-4861-mexico
    # Notes: F1 store uses "Main Grandstand 1", "Grandstand 4",
    #   "Grandstand 5", "Grandstand 6", "Grandstands 14 and 15",
    #   "General Admission 6A", "Grandstand 7", etc.
    #   Our DB adds parenthetical location descriptors.
    # =========================================================================
    "Autodromo Hermanos Rodriguez": {
        "Grandstand Main 1": "Main Grandstand 1",
        "Grandstand 4 (Turns 1-3)": "Grandstand 4",
        "Grandstand 5 (Turns 1-3)": "Grandstand 5",
        "Grandstand 6 (Back Straight)": "Grandstand 6",
        "Grandstand 6A": "General Admission 6A",
        "Grandstand 3A": "Grandstand 3A",
        "Grandstand 14 (Stadium Section)": "Grandstands 14 and 15",
        "Grandstand 15 (Stadium Section)": "Grandstand 15",
        "Grandstand 5A (Turns 2-3)": "Grandstand 5A",
        "Grandstand 2A": "Grandstand 2A",
        "General Admission": "General Admission",
    },
    # =========================================================================
    # 19. Interlagos (Sao Paulo, Brazil)
    # F1 store: tickets.formula1.com/en/f1-3325-brazil
    # Notes: F1 store uses "Grandstand R", "Grandstand D", etc.
    #   Our DB adds parenthetical track-location descriptions.
    # =========================================================================
    "Interlagos": {
        "Grandstand M (Main Straight)": "Grandstand M",
        "Grandstand A (Finish Straight)": "Grandstand A",
        "Grandstand D (Senna S)": "Grandstand D",
        "Grandstand G (Reta Oposta)": "Grandstand G",
        "Grandstand H (Esses)": "Grandstand H",
        "Grandstand V (Turn 4 - Descida do Lago)": "Grandstand V",
        "Grandstand B (Main Straight)": "Grandstand B",
        "Grandstand N (Esses)": "Grandstand N",
        "Grandstand R (Reta Oposta)": "Grandstand R",
        "Grandstand S (Reta Oposta)": "Grandstand S",
        "General Admission": "General Admission",
    },
    # =========================================================================
    # 20. Las Vegas Street Circuit (USA)
    # F1 store: tickets.formula1.com/en/f1-59007-las-vegas
    # Notes: F1 store uses "Heineken Silver Main Grandstand",
    #   "Grandstand Lewis Hamilton", "T-Mobile Zone at Sphere",
    #   "Turn 3 Grandstand", "West Harmon Grandstand",
    #   "General Admission". Names are very similar to ours.
    # =========================================================================
    "Las Vegas Street Circuit": {
        "Heineken Silver Main Grandstand": "Heineken Silver Main Grandstand",
        "Grandstand SG1 Sphere": "T-Mobile Zone at Sphere Grandstand SG1",
        "T-Mobile Grandstand": "T-Mobile Grandstand",
        "West Harmon Grandstand": "West Harmon Grandstand",
        "Turn 3 Grandstand": "Turn 3 Grandstand",
        "Lewis Hamilton Grandstand": "Grandstand Lewis Hamilton",
        "Grandstand SG7 Sphere": "T-Mobile Zone at Sphere Grandstand SG7",
        "General Admission - T-Mobile Zone": "General Admission (T-Mobile Zone)",
        "General Admission - Flamingo Zone": "General Admission (Flamingo Zone)",
        "General Admission - Caesars Palace Experience": "General Admission (Caesars Palace)",
    },
    # =========================================================================
    # 21. Losail International Circuit (Qatar)
    # F1 store: tickets.formula1.com/en/f1-56257-qatar
    # Notes: F1 store uses "Main Grandstand", "North Grandstand",
    #   "T2 Grandstand", "T3 Grandstand", "T16 Grandstand".
    #   Our DB uses "Podium & Main Grandstand" and "Nord Grandstand".
    # =========================================================================
    "Losail International Circuit": {
        "Podium & Main Grandstand": "Main Grandstand",
        "Nord Grandstand": "North Grandstand",
        "Grandstand T2": "T2 Grandstand",
        "Grandstand T3": "T3 Grandstand",
        "Grandstand T16": "T16 Grandstand",
        "General Admission": "General Admission",
    },
    # =========================================================================
    # 22. Yas Marina Circuit (Abu Dhabi, UAE)
    # F1 store: tickets.formula1.com/en/f1-3312-abu-dhabi
    # Notes: F1 store uses "Main Grandstand", "North Grandstand",
    #   "West Grandstand", "South Grandstand", "Marina Grandstand",
    #   "Abu Dhabi Hill (General Admission)", "North Premium",
    #   "West Social Club". Names mostly match with minor differences.
    # =========================================================================
    "Yas Marina Circuit": {
        "Grandstand Main": "Main Grandstand",
        "Grandstand West": "West Grandstand",
        "Grandstand Nord": "North Grandstand",
        "Grandstand South": "South Grandstand",
        "Grandstand Marina": "Marina Grandstand",
        "Grandstand West Straight": "West Straight Grandstand",
        "Grandstand North Straight": "North Straight Grandstand",
        "General Admission - Abu Dhabi Hill": "Abu Dhabi Hill",
    },
}


# Reverse lookup: given an F1 store name, find our DB name.
# {circuit_name: {f1_store_name: our_db_name}}
def build_reverse_aliases() -> dict[str, dict[str, str]]:
    """Build a reverse mapping from F1 store names to our DB section names."""
    reverse: dict[str, dict[str, str]] = {}
    for circuit, aliases in F1_STORE_ALIASES.items():
        reverse[circuit] = {}
        for our_name, store_name in aliases.items():
            # Multiple DB names can map to the same store name (e.g. COTA
            # Main Grandstand tiers), so we keep the first one found.
            if store_name not in reverse[circuit]:
                reverse[circuit][store_name] = our_name
    return reverse


REVERSE_ALIASES = build_reverse_aliases()
