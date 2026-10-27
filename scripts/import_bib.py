#!/usr/bin/env python3
"""One-time migration: build content/publication/* and content/talk/* from the
legacy Quarto site's pubs.bib plus the C.V. (Jan. 15, 2026).

This script is only needed for the initial migration. After that, edit the
Markdown files in content/ directly (see UPDATING.md).
"""
import json, re, os, textwrap
import bibtexparser
from bibtexparser.bparser import BibTexParser

BIB = "/home/claude/nowlin-site/pubs.bib"
OUT = "/home/claude/site/content"

p = BibTexParser(common_strings=True)
db = {e["ID"]: e for e in bibtexparser.load(open(BIB), parser=p).entries}

ME = "Matthew C. Nowlin"

# Each entry: slug, bib key (or None), C.V. title, authors (C.V. order and spelling),
# type, tab, venue override, year override, areas (research-area ids), notes (HTML comments)
PUBS = [
 # ---- Books
 dict(slug="environmental-policymaking-in-an-era-of-climate-change", key="nowlinEnvironmentalPolicymakingEra2019",
      title="Environmental Policymaking in an Era of Climate Change", authors=[ME], type="book", tab="book",
      venue="New York, NY: Routledge", areas=["policy-process","climate-energy"], featured=True),
 # ---- Journal articles
 dict(slug="sea-level-rise-adaptation-polycentric-governance", key="vantaggiatoSeaLevelRiseAdaptation2026",
      title="Sea-Level Rise Adaptation and Collaboration in Polycentric Governance: A Comparison of Three Regions",
      authors=["Francesca Vantaggiato","Mark Lubell",ME,"Juita-Elena (Wie) Yusuf","Majid Shafiee-Jood"],
      venue="Public Administration Review, Forthcoming", forthcoming=True, areas=["climate-energy","governance"]),
 dict(slug="deciding-who-decides", key="nowlinDecidingWhoDecides2026",
      title="Deciding Who Decides: Trust and Support for Elected Official, Expert, and Citizen Decision-Making Regarding Nuclear Waste Management",
      authors=[ME,"Chris Anderson","Justin Reedy"], venue="Review of Policy Research, 43(1)", areas=["nuclear","deliberation"], featured=True),
 dict(slug="policy-beliefs-belief-uncertainty-policy-learning", key="nowlinPolicyBeliefsBelief2024",
      title="Policy Beliefs, Belief Uncertainty, and Policy Learning Through the Lens of the Advocacy Coalition Framework",
      authors=[ME], venue="Policy and Politics, 52(4): 675–695", areas=["policy-process"], sub="learning", featured=True),
 dict(slug="stormwater-pond-buffer-implementation", key="cannonIdentifyingBarriersPreventing2024",
      title="Identifying Barriers Preventing Stormwater Pond Buffer Implementation in Coastal South Carolina",
      authors=["Sean Cannon","Abigail Prochaska","Kendra Stewart","Timothy Callahan",ME],
      venue="Journal of South Carolina Water Resources, 9(2)", areas=["governance"], students=["Sean Cannon"]),
 dict(slug="technical-issues-and-engagement-processes", key="reedyTechnicalIssuesEngagement2023",
      title="Technical Issues and Engagement Processes: Support for Citizen and Expert Deliberation Regarding the Management of Nuclear Waste",
      authors=["Justin Reedy","Chris Anderson",ME], venue="Frontiers in Communication, 8", areas=["nuclear","deliberation"], students=["Chris Anderson"]),
 dict(slug="routine-weather-information-usage", key="wehdeDeterminingPatternsRoutine2023",
      title="Determining Patterns of Routine Weather Information Usage and Their Demographic Determinants",
      authors=["Wesley Wehde",ME], venue="Weather, Climate, and Society, 15(3): 711–725", areas=["hazards"]),
 dict(slug="scaling-up-deliberative-mini-publics", key="rountreeInternalDynamicsScaling2022a",
      title="The Internal Dynamics of ‘Scaling Up’ Deliberative Mini-Publics",
      authors=["John Rountree","Chris Anderson","Justin Reedy",ME], venue="Communication and the Public, 7(3): 146–164",
      areas=["deliberation"], students=["Chris Anderson"]),
 dict(slug="who-should-do-more-about-climate-change", key="nowlinWhoShouldMore2022",
      title="Who Should ‘Do More’ about Climate Change? Cultural Theory, Polycentricity, and Public Support for Climate Change Actions across Actors and Governments",
      authors=[ME], venue="Review of Policy Research, 39(4): 468–485", areas=["cultural-theory","climate-energy","governance"], featured=True),
 dict(slug="advocacy-coalitions-and-political-control", key="nowlinAdvocacyCoalitionsPolitical2022",
      title="Advocacy Coalitions and Political Control", authors=[ME,"Maren Trochmann","Thomas M. Rabovsky"],
      venue="Politics and Policy, 50(2): 201–224", areas=["policy-process"], sub="change"),
 dict(slug="climate-science-or-politics", key="hawesClimateSciencePolitics2022",
      title="Climate Science or Politics? Disentangling the Roles of Citizen Beliefs and Support for Energy in the United States",
      authors=["Rachel Hawes",ME], venue="Energy Research and Social Science, 85", areas=["climate-energy"], students=["Rachel Hawes"]),
 dict(slug="policy-learning-and-information-processing", key="nowlinPolicyLearningInformation2021",
      title="Policy Learning and Information Processing", authors=[ME], venue="Policy Studies Journal, 49(4): 1019–1039",
      areas=["policy-process"], sub="learning", featured=True),
 dict(slug="social-capital-and-hurricane-warning-response", key="nowlinSocialCapitalHurricane2021",
      title="Social Capital and Hurricane Warning Response", authors=[ME,"Wesley Wehde"],
      venue="International Journal of Disaster Risk Reduction, 65", areas=["hazards"], featured=True),
 dict(slug="political-beliefs-technocracy-energy-climate", key="nowlinPoliticalBeliefsViews2021",
      title="Political Beliefs, Views about Technocracy, and Energy and Climate Policy Preferences", authors=[ME],
      venue="Public Understanding of Science, 30(3): 331–348", areas=["climate-energy","deliberation"]),
 dict(slug="public-attribution-of-responsibility-disaster-preparedness", key="wehdePublicAttributionResponsibility2021",
      title="Public Attribution of Responsibility for Disaster Preparedness across Three Levels of Government and the Public: Lessons from a Survey of Residents of the U.S. South Atlantic and Gulf Coast Areas",
      authors=["Wesley Wehde",ME], venue="Publius: The Journal of Federalism, 51(2): 212–237", areas=["hazards","governance"],
      notes=["The C.V. spells the first author 'Welsey Wehde' here; corrected to 'Wesley Wehde' to match the BibTeX and his other papers."]),
 dict(slug="place-values-and-public-opinion-about-climate-change", key="bundrickPlaceValuesPublic2020",
      title="Place, Values, and Public Opinion About Climate Change in South Carolina", authors=["M. Lee Bundrick Jr.",ME],
      venue="Journal of Political Science, 48(1): 85–109", areas=["climate-energy","cultural-theory"], students=["M. Lee Bundrick Jr."],
      notes=["The C.V. lists this as volume 40; the BibTeX and the journal URL (vol48/iss1) say volume 48. Shown as 48 — please confirm."]),
 dict(slug="revenue-use-and-public-support-for-a-carbon-tax", key="nowlinRevenueUsePublic2020",
      title="Revenue Use and Public Support for a Carbon Tax", authors=[ME,"Kuhika Gupta","Joseph T. Ripberger"],
      venue="Environmental Research Letters, 15(8)", areas=["climate-energy"], featured=True),
 dict(slug="cultural-theory-of-partisanship-and-policy-attitudes", key="nowlinCulturalTheoryPartisanship2020",
      title="A Cultural Theory of Partisanship and Policy Attitudes", authors=[ME,"Thomas M. Rabovsky"],
      venue="Social Science Quarterly, 101(2): 878–892", areas=["cultural-theory"], featured=True),
 dict(slug="tracking-the-nuclear-mood", key="guptaTrackingNuclearMood2019",
      title="Tracking the Nuclear ‘Mood’ in the United States: Introducing a Long-Term Measure of Public Opinion about Nuclear Energy Using Aggregate Survey Data",
      authors=["Kuhika Gupta",ME,"Joseph T. Ripberger","Hank C. Jenkins-Smith","Carol L. Silva"], venue="Energy Policy, 133",
      areas=["nuclear","climate-energy"], featured=True),
 dict(slug="hot-rocks-that-shoot-ghost-bullets", key="nowlinHotRocksThat2019",
      title="‘Hot Rocks that Shoot Ghost Bullets’: Native American Perceptions of a Nuclear Waste Facility",
      authors=[ME,"Thaddieus W. Conner"], venue="Politics, Groups, and Identities, 7(1): 21–38", areas=["nuclear"]),
 dict(slug="cultural-theory-and-managerial-values", key="connerCulturalTheoryManagerial2016",
      title="Cultural Theory and Managerial Values: Examining Trust as a Motivation for Collaboration",
      authors=["Thaddieus W. Conner",ME,"Thomas M. Rabovsky","Joseph T. Ripberger"], venue="Public Administration, 94(4): 915–932",
      areas=["cultural-theory","governance"]),
 dict(slug="modeling-issue-definitions-using-quantitative-text-analysis", key="nowlinModelingIssueDefinitions2016",
      title="Modeling Issue Definitions using Quantitative Text Analysis", authors=[ME], venue="Policy Studies Journal, 44(3): 309–331",
      areas=["policy-process","methods"], sub="change"),
 dict(slug="policy-change-policy-feedback-interest-mobilization", key="nowlinPolicyChangePolicy2016",
      title="Policy Change, Policy Feedback, and Interest Mobilization: The Politics of Nuclear Waste Management", authors=[ME],
      venue="Review of Policy Research, 33(1): 51–70", areas=["policy-process","nuclear"], sub="change"),
 dict(slug="cultural-theory-political-ideology-political-knowledge", key="ripbergerReconsideringRelationshipCultural2012",
      title="Reconsidering the Relationship Between Cultural Theory, Political Ideology, and Political Knowledge",
      authors=["Joseph T. Ripberger","Geoboo Song",ME,"Michael D. Jones","Hank C. Jenkins-Smith"],
      venue="Social Science Quarterly, 93(3): 713–731", areas=["cultural-theory"]),
 dict(slug="weather-climate-and-worldviews", key="goebbertWeatherClimateWorldviews2012",
      title="Weather, Climate and Worldviews: The Sources and Consequences of Public Perceptions of Changes in Local Weather Patterns",
      authors=["Kevin Goebbert","Hank C. Jenkins-Smith","Kim Klockow",ME,"Carol L. Silva"], venue="Weather, Climate, and Society, 4(2): 132–144",
      areas=["cultural-theory","hazards","climate-energy"]),
 dict(slug="theories-of-the-policy-process", key="nowlinTheoriesPolicyProcess2011",
      title="Theories of the Policy Process: State of the Research and Emerging Trends", authors=[ME],
      venue="Policy Studies Journal, 39(s1): 41–60", areas=["policy-process"], sub="theories", featured=True,
      body="Excerpted in: Theodoulou, Stella Z., and Matthew A. Cahn (eds). 2013. *Public Policy: The Essential Readings*. 2nd Edition. New York, NY: Pearson, 190–195."),
 dict(slug="reversing-nuclear-opposition", key="jenkins-smithReversingNuclearOpposition2011",
      title="Reversing Nuclear Opposition: Evolving Public Acceptance of a Permanent Nuclear Waste Disposal Facility",
      authors=["Hank C. Jenkins-Smith","Carol L. Silva",ME,"Grant deLozier"], venue="Risk Analysis, 31(4): 629–644", areas=["nuclear"],
      notes=["The C.V. repeats 'Carol L.' after Carol L. Silva in this author list; treated as a typo."]),
 dict(slug="oklahoma-marriage-initiative-implementation", key="nowlinImplementationOklahomaMarriage2008",
      title="The Implementation of the Oklahoma Marriage Initiative to Individuals Receiving Temporary Assistance for Needy Families",
      authors=[ME], venue="Oklahoma Politics, 17: 111–131", areas=["policy-process"], sub="change",
      notes=["The C.V. gives volume 17; the BibTeX gives volume 18. Shown as 17 (C.V.) — please confirm."]),
 # ---- Book chapters
 dict(slug="policy-learning-as-belief-updating", key="nowlinPolicyLearningBelief2026",
      title="Policy Learning as Belief Updating through Information Processing", authors=[ME], type="chapter", tab="chapters",
      venue="In Handbook of Policy Learning, eds. Claudio M. Radaelli and Bishoy L. Zaki. Edward Elgar Publishing, Forthcoming",
      forthcoming=True, areas=["policy-process"], sub="learning"),
 dict(slug="learning-and-uncertainty", key="nowlinLearningUncertaintyInformation2025",
      title="Learning and Uncertainty: Information Environments and Policy-Oriented Learning", authors=[ME], type="chapter", tab="chapters",
      venue="In The Advocacy Coalition Framework, eds. Hank Jenkins-Smith and Christopher Weible. Palgrave Macmillan, 155–182",
      areas=["policy-process"], sub="learning"),
 dict(slug="teaching-quantitative-methods-to-students-of-public-policy", key="nowlinTeachingQuantitativeMethods2024",
      title="Teaching Quantitative Methods to Students of Public Policy", authors=[ME,"Wesley Wehde"], type="chapter", tab="chapters",
      venue="In Handbook of Teaching Public Policy, eds. Philippe Zittoun and Emily St Denny. Edward Elgar Publishing, 168–180",
      areas=["methods"]),
 # ---- Proceedings
 dict(slug="partisanship-information-and-public-opinion-about-yucca-mountain", key="nowlinPartisanshipInformationPublic2015",
      title="Partisanship, Information, and Public Opinion about Yucca Mountain", authors=[ME], type="conference_paper", tab="proceedings",
      venue="In Proceedings of the 15th International High-Level Radioactive Waste Management Conference, 226–231. American Nuclear Society",
      areas=["nuclear"]),
 # ---- Book reviews
 dict(slug="improving-governance-of-risk-and-uncertainty", key="nowlinImprovingGovernanceRisk2018",
      title="Improving Governance of Risk and Uncertainty", authors=[ME], type="book_review", tab="reviews", year=2018,
      venue="Journal of Public Administration Research and Theory, 28(1): 158–160", areas=["governance"],
      notes=["The BibTeX dates this 2017 (online first); the C.V. gives 2018 (print). Shown as 2018."]),
 # ---- Open-source educational resources
 dict(slug="quantitative-research-methods-for-political-science", key="jenkins-smithQuantitativeResearchMethods2017",
      title="Quantitative Research Methods for Political Science, Public Policy, and Public Administration",
      authors=["Hank C. Jenkins-Smith","Joseph T. Ripberger","Gary Copeland",ME,"Tyler Hughes","Aaron L. Fister","Wesley Wehde"],
      type="book", tab="oer", venue="University Libraries, University of Oklahoma. SHAREOK, Open Education Resource", areas=["methods"]),
]

TALKS = [
 ("environmental-policymaking-process-and-evolution", "Environmental Policymaking: Process and Evolution", "2025-02-01",
  "City University of New York, Environmental Policymaking graduate course", "Virtual", ["policy-process","climate-energy"]),
 ("environmental-policy-politics-and-polarization", "Environmental Policy, Politics, and Polarization", "2024-10-01",
  "Panel discussion, “Environmental Policy and the Impact of Elections,” College of Charleston", "Charleston, SC", ["climate-energy"]),
 ("institutions-and-actors-in-us-climate-policy", "Institutions and Actors in US Climate Policy", "2024-04-01",
  "City University of New York, Environmental Policymaking graduate course", "Virtual", ["climate-energy","governance"]),
 ("beliefs-about-climate-change", "Beliefs about Climate Change", "2023-09-01",
  "Center for Coastal Physical Oceanography and Institute for Coastal Adaptation & Resilience, Old Dominion University, Fall 2023 Virtual Seminar Series",
  "Virtual", ["climate-energy","cultural-theory"]),
 ("deliberative-processes-stakeholder-engagement", "Deliberative Processes as a Tool for Stakeholder Engagement", "2022-05-01",
  "S.C. Sea Grant Consortium Research Symposium", "Charleston, SC", ["deliberation"]),
 ("public-opinion-about-climate-change-in-south-carolina", "Public Opinion About Climate Change in South Carolina", "2019-11-01",
  "Coastal and Environmental Law Summit", "Charleston, SC", ["climate-energy"]),
 ("climate-change-science-policy-and-politics", "Climate Change: Science, Policy, and Politics", "2019-10-15",
  "Science Cafe, Charleston County Public Library, Hurd/St. Andrews Branch", "Charleston, SC", ["climate-energy"]),
 ("carbon-tax-and-public-opinion", "Carbon Tax and Public Opinion", "2019-10-01",
  "Panel discussion, “Climate Change: Is A Carbon Tax A Solution,” College of Charleston", "Charleston, SC", ["climate-energy"]),
 ("the-policy-and-politics-of-climate-change", "The Policy and Politics of Climate Change", "2017-11-01",
  "Charleston County Democratic Women", "Charleston, SC", ["climate-energy"]),
 ("understanding-climate-change", "Understanding Climate Change", "2017-08-01",
  "Charleston County Public Library", "Charleston, SC", ["climate-energy"]),
]

def clean_abs(a):
    if not a: return ""
    a = re.sub(r"\s+", " ", a).strip()
    a = re.sub(r"^Abstract\.?\s*", "", a)
    a = re.sub(r"^Objective\s*", "Objective: ", a)
    a = a.replace("\\&", "&").replace("{", "").replace("}", "").replace("--", "–")
    # Social Science Quarterly structured abstracts run headings into text
    a = re.sub(r"\b(Methods|Results|Conclusions?)(?=[A-Z])", r" \1: ", a)
    return re.sub(r"\s+", " ", a).strip()

def y(s): return json.dumps(s, ensure_ascii=False)

def date_of(e, item):
    if item.get("year"): return f"{item['year']}-01-01"
    d = (e or {}).get("date", "") or ""
    m = re.match(r"(\d{4})(?:-(\d{2}))?(?:-(\d{2}))?", d)
    if not m: return "2000-01-01"
    return f"{m.group(1)}-{m.group(2) or '01'}-{m.group(3) or '01'}"

os.makedirs(f"{OUT}/publication", exist_ok=True)
legacy = {}
for it in PUBS:
    e = db.get(it["key"]) if it.get("key") else None
    typ = it.get("type", "journal_article"); tab = it.get("tab", "articles")
    legacy[it["slug"]] = {"tab": tab, "legacy": {"articles":"Journal Articles","book":"Books","chapters":"Book Chapters",
        "proceedings":"Refereed Conference Proceedings","reviews":"Book Reviews","oer":"Open-Source Educational Resources"}[tab]}
    links = []
    doi = (e or {}).get("doi", "")
    if doi: links.append({"name": "Publisher's Version", "url": f"https://doi.org/{doi}"})
    elif (e or {}).get("url"): links.append({"name": "Publisher's Version", "url": e["url"]})
    if it["slug"] == "quantitative-research-methods-for-political-science":
        links = [{"name": "Open Textbook", "url": "https://shareok.org/handle/11244/52244"},
                 {"name": "DOI", "url": "https://doi.org/10.15763/11244/52244"}]
    fm = ["---", f"title: {y(it['title'])}", f"date: {date_of(e, it)}",
          "authors: [" + ", ".join(y(a) for a in it["authors"]) + "]",
          f"publication_types: [{y(typ)}]", f"publication: {y(it['venue'])}"]
    if it.get("forthcoming"): fm.append("status: forthcoming")
    if it.get("students"): fm.append("student_authors: [" + ", ".join(y(a) for a in it["students"]) + "]")
    ab = clean_abs((e or {}).get("abstract"))
    if ab: fm.append(f"abstract: {y(ab)}")
    if doi: fm.append(f"doi: {y(doi)}")
    if links:
        fm.append("links:")
        for l in links: fm += [f"  - name: {y(l['name'])}", f"    url: {y(l['url'])}"]
    fm.append("tags: [" + ", ".join(y(a) for a in it["areas"]) + "]")
    if it.get("featured"): fm.append("featured: true")
    fm.append("---")
    body = ""
    for n in it.get("notes", []): body += f"<!-- NOTE FOR MATT: {n} -->\n"
    if it.get("body"): body += "\n" + it["body"] + "\n"
    d = f"{OUT}/publication/{it['slug']}"; os.makedirs(d, exist_ok=True)
    open(f"{d}/index.md", "w").write("\n".join(fm) + "\n" + body)

os.makedirs(f"{OUT}/talk", exist_ok=True)
for slug, title, date, event, loc, areas in TALKS:
    d = f"{OUT}/talk/{slug}"; os.makedirs(d, exist_ok=True)
    open(f"{d}/index.md", "w").write("\n".join(["---", f"title: {y(title)}", f"date: {date}", f"authors: [{y(ME)}]",
        'publication_types: ["presentation"]', f"event: {y(event)}", f"location: {y(loc)}",
        f"publication: {y(event + ', ' + loc)}", "talk_type: Invited talk",
        "tags: [" + ", ".join(y(a) for a in areas) + "]", "---", ""]))

json.dump({"entries": legacy}, open("/home/claude/site/data/writings_legacy_map.json", "w"), indent=2, ensure_ascii=False)

# Research areas -> subcategories -> slugs (drives homepage accordions, the area filter, and See Also siblings)
AREAS = [
 ("policy-process", "Theories of the Policy Process",
  "How policy changes and how policy actors learn: the Advocacy Coalition Framework, policy learning as belief updating, information processing, policy feedback, and implementation.",
  [("theories", "Theories and Frameworks"), ("learning", "Policy Learning and Information Processing"), ("change", "Coalitions, Policy Change, and Implementation")]),
 ("cultural-theory", "Cultural Theory and Political Beliefs",
  "Belief systems and worldviews — particularly the cultural theory of risk — and how they shape partisanship, policy attitudes, trust, and perceptions of risk.", []),
 ("climate-energy", "Climate Change and Energy Policy",
  "Public opinion about climate change and energy, support for carbon pricing, and the politics of U.S. climate and energy policy.", []),
 ("nuclear", "Nuclear Energy and Nuclear Waste",
  "Public acceptance of nuclear energy and nuclear waste facilities, trust in decision-makers, and the politics of nuclear waste management.", []),
 ("hazards", "Natural Hazards and Weather",
  "How people use weather information and respond to hurricane warnings, and who the public holds responsible for disaster preparedness.", []),
 ("deliberation", "Deliberation, Trust, and Expertise",
  "Citizen deliberation and mini-publics, technocracy, and public support for citizen, expert, and elected-official decision-making.", []),
 ("governance", "Environmental Governance and Collaboration",
  "Polycentric governance, collaboration among public managers and stakeholders, and coastal adaptation to sea-level rise.", []),
 ("methods", "Research Methods and Teaching",
  "Quantitative text analysis, open educational resources for quantitative methods, and teaching methods to students of public policy.", []),
]
out = []
for aid, title, desc, subs in AREAS:
    members = [it["slug"] for it in PUBS if aid in it["areas"]] + [t[0] for t in TALKS if aid in t[5]]
    a = {"id": aid, "title": title, "description": desc, "items": members, "subcategories": []}
    for sid, stitle in subs:
        a["subcategories"].append({"id": f"{aid}--{sid}", "title": stitle,
            "items": [it["slug"] for it in PUBS if aid in it["areas"] and it.get("sub") == sid]})
    out.append(a)
json.dump({"areas": out}, open("/home/claude/site/data/research_areas.json", "w"), indent=2, ensure_ascii=False)
print(len(PUBS), "publications,", len(TALKS), "talks")
