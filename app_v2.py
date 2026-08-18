import streamlit as st
import pandas as pd


# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="DIAMOND | MOVEᴱ",
    page_icon="💎",
    layout="wide"
)


# ============================================================
# DIAMOND VISUAL IDENTITY
# ============================================================

st.markdown(
    """
    <style>
    :root {
        --diamond-navy: #062B4F;
        --diamond-teal: #20B8BE;
        --diamond-aqua: #9DEBE7;
        --diamond-light: #F4FAFA;
        --diamond-grey: #66727D;
    }

    .stApp {
        background-color: #FFFFFF;
    }

    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #F2FAFA 0%, #FFFFFF 100%);
        border-right: 1px solid #DCEBEC;
    }

    h1, h2, h3 {
        color: var(--diamond-navy);
    }

    [data-testid="stMetricValue"] {
        color: var(--diamond-navy);
    }

    div[data-testid="stAlert"] {
        border-radius: 10px;
    }

    .stButton > button[kind="primary"] {
        background-color: var(--diamond-teal);
        border-color: var(--diamond-teal);
        color: white;
    }

    .stButton > button[kind="primary"]:hover {
        background-color: #169EA4;
        border-color: #169EA4;
        color: white;
    }

    .stButton > button:not([kind="primary"]) {
        border-color: var(--diamond-teal);
        color: var(--diamond-navy);
    }

    .diamond-kicker {
        color: #20B8BE;
        font-weight: 700;
        letter-spacing: 0.08em;
        text-transform: uppercase;
        font-size: 0.82rem;
        margin-bottom: 0.25rem;
    }

    .diamond-subtitle {
        color: #66727D;
        font-size: 1.05rem;
        margin-top: -0.35rem;
        margin-bottom: 1.2rem;
    }

    .prototype-note {
        background: #F2FAFA;
        border-left: 4px solid #20B8BE;
        padding: 0.8rem 1rem;
        border-radius: 6px;
        margin: 0.8rem 0 1.2rem 0;
        color: #294653;
    }
    </style>
    """,
    unsafe_allow_html=True
)


# ============================================================
# LOAD BASE DATA
# ============================================================

@st.cache_data
def load_data():

    jobseekers = pd.read_pickle(
        "jobseekers.pkl"
    )

    courses = pd.read_pickle(
        "courses.pkl"
    )

    labour_market = pd.read_pickle(
        "labour_market.pkl"
    )

    return (
        jobseekers,
        courses,
        labour_market
    )


jobseekers, courses, labour_market = load_data()

# ============================================================
# SELECT JOBSEEKER
# ============================================================

user_options = (
    jobseekers["user_id"]
    .sort_values()
    .tolist()
)

selected_user_id = st.sidebar.selectbox(
    "Select simulated jobseeker",
    options=user_options
)

selected_user = (
    jobseekers[
        jobseekers["user_id"] == selected_user_id
    ]
    .iloc[0]
)


# ============================================================
# APP VIEW
# ============================================================

page_mode = st.sidebar.radio(
    "View",
    options=[
        "Recommended learning",
        "Course catalogue",
        "My ᴱGROW profile"
    ],
    index=0
)


# ============================================================
# SESSION STATE
# ============================================================

if "interested_courses" not in st.session_state:
    st.session_state.interested_courses = []

if "viewed_course" not in st.session_state:
    st.session_state.viewed_course = None

# Reset user-specific UI state when another simulated user is selected
if "active_user_id" not in st.session_state:
    st.session_state.active_user_id = selected_user_id

elif st.session_state.active_user_id != selected_user_id:
    st.session_state.active_user_id = selected_user_id
    st.session_state.interested_courses = []
    st.session_state.viewed_course = None


# ============================================================
# HELPER FUNCTIONS
# ============================================================

def mark_interested(course_id):
    if course_id not in st.session_state.interested_courses:
        st.session_state.interested_courses.append(course_id)


def open_course(course_id):
    st.session_state.viewed_course = course_id


def close_course():
    st.session_state.viewed_course = None


# ============================================================
# USER SELECTION
# ============================================================

user_id = selected_user_id

# Basic selected-user information
digital_profile = selected_user["digital_profile"]
green_profile = selected_user["green_profile"]
target_role = selected_user["target_role"]
preferred_language = selected_user["preferred_language"]
delivery_preference = selected_user["delivery_preference"]

# ============================================================
# PROFILE EXTRACTION
# ============================================================

from dataclasses import dataclass, field
from typing import Optional


@dataclass
class JobSeekerProfile:

    user_id: str

    digital_class: int
    digital_profile: str
    digital_level: str

    green_class: int
    green_profile: str

    age: Optional[int]
    country: Optional[str]
    city: Optional[str]
    preferred_language: Optional[str]

    education_level: Optional[str]
    employment_status: Optional[str]
    program_status: Optional[str]

    skills: list = field(default_factory=list)
    target_role: Optional[str] = None
    work_history: list = field(default_factory=list)

    availability: Optional[str] = None
    delivery_preference: Optional[str] = None
    transport_limitations: Optional[str] = None

    accessibility_need: Optional[str] = None

    previous_courses: list = field(default_factory=list)

    motivation_level: Optional[str] = None
    case_notes: Optional[str] = None
    cv_text: Optional[str] = None

    missing_fields: list = field(default_factory=list)
    conflicts_found: list = field(default_factory=list)

    profile_confidence: str = "low"

    can_recommend: bool = False

    recommendation_blockers: list = field(
        default_factory=list
    )


CRITICAL_PROFILE_FIELDS = [
    "digital_profile",
    "green_profile",
    "target_role",
    "preferred_language",
    "delivery_preference"
]


def extract_jobseeker_profile(user):

    missing_fields = []

    for field_name in CRITICAL_PROFILE_FIELDS:

        value = user.get(field_name, None)

        if (
            value is None
            or pd.isna(value)
            or value == ""
        ):
            missing_fields.append(field_name)

    conflicts = []

    questionnaire = user.get(
        "questionnaire_answers",
        {}
    )

    platform = user.get(
        "platform_profile",
        {}
    )

    questionnaire_language = questionnaire.get(
        "preferred_language"
    )

    platform_language = platform.get(
        "preferred_language"
    )

    if (
        questionnaire_language is not None
        and platform_language is not None
        and questionnaire_language != platform_language
    ):
        conflicts.append(
            "Preferred language differs between questionnaire "
            "and platform profile."
        )

    questionnaire_delivery = questionnaire.get(
        "delivery_preference"
    )

    platform_delivery = platform.get(
        "delivery_preference"
    )

    if (
        questionnaire_delivery is not None
        and platform_delivery is not None
        and questionnaire_delivery != platform_delivery
    ):
        conflicts.append(
            "Delivery preference differs between questionnaire "
            "and platform profile."
        )

    if len(missing_fields) == 0 and len(conflicts) == 0:
        profile_confidence = "high"

    elif len(missing_fields) <= 1 and len(conflicts) <= 1:
        profile_confidence = "medium"

    else:
        profile_confidence = "low"

    blockers = []

    if missing_fields:
        blockers.append(
            "Missing critical information: "
            + ", ".join(missing_fields)
        )

    if profile_confidence == "low":
        blockers.append(
            "Profile confidence is too low."
        )

    can_recommend = len(blockers) == 0

    profile = JobSeekerProfile(

        user_id=user["user_id"],

        digital_class=int(
            user["latent_class_digital"]
        ),

        digital_profile=user["digital_profile"],

        digital_level=user["digital_level"],

        green_class=int(
            user["latent_class_green"]
        ),

        green_profile=user["green_profile"],

        age=int(user["age"])
        if pd.notna(user["age"])
        else None,

        country=user["country"],

        city=user["city"],

        preferred_language=user[
            "preferred_language"
        ],

        education_level=user[
            "education_level"
        ],

        employment_status=user[
            "employment_status"
        ],

        program_status=user[
            "program_status"
        ],

        skills=user["skills"],

        target_role=user["target_role"],

        work_history=user[
            "work_history"
        ],

        availability=user[
            "availability"
        ],

        delivery_preference=user[
            "delivery_preference"
        ],

        transport_limitations=user[
            "transport_limitations"
        ],

        accessibility_need=user[
            "accessibility_need"
        ],

        previous_courses=user[
            "previous_courses"
        ],

        motivation_level=user[
            "motivation_level"
        ],

        case_notes=user[
            "case_notes"
        ],

        cv_text=user[
            "cv_text"
        ],

        missing_fields=missing_fields,

        conflicts_found=conflicts,

        profile_confidence=profile_confidence,

        can_recommend=can_recommend,

        recommendation_blockers=blockers
    )

    return profile

profile = extract_jobseeker_profile(
    selected_user
)


# ============================================================
# COURSE RETRIEVAL
# ============================================================

def retrieve_candidate_courses(
    profile,
    courses,
    max_candidates=30
):

    candidate_courses = courses.copy()

    # --------------------------------------------------------
    # Target-role match
    # --------------------------------------------------------

    candidate_courses["target_role_match"] = (
        candidate_courses["target_role"]
        .str.lower()
        .eq(
            str(profile.target_role).lower()
        )
    )

    # --------------------------------------------------------
    # Skill overlap
    # --------------------------------------------------------

    user_skills = {
        str(skill).lower()
        for skill in profile.skills
    }

    candidate_courses["skill_overlap"] = (
        candidate_courses["skills_taught"]
        .apply(
            lambda skills: len(
                user_skills.intersection(
                    {
                        str(skill).lower()
                        for skill in skills
                    }
                )
            )
            if isinstance(skills, list)
            else 0
        )
    )

    # --------------------------------------------------------
    # Retrieval score
    # --------------------------------------------------------

    candidate_courses["retrieval_score"] = (
        candidate_courses[
            "target_role_match"
        ].astype(int) * 2
        +
        candidate_courses[
            "skill_overlap"
        ]
    )

    # --------------------------------------------------------
    # Keep relevant candidates
    # --------------------------------------------------------

    relevant_courses = candidate_courses[
        candidate_courses[
            "retrieval_score"
        ] > 0
    ].copy()

    # Fallback if there are no direct matches
    if relevant_courses.empty:

        relevant_courses = (
            candidate_courses
            .sort_values(
                "retrieval_score",
                ascending=False
            )
            .head(max_candidates)
            .copy()
        )

    else:

        relevant_courses = (
            relevant_courses
            .sort_values(
                "retrieval_score",
                ascending=False
            )
            .head(max_candidates)
            .copy()
        )

    return relevant_courses

candidate_courses = retrieve_candidate_courses(
    profile=profile,
    courses=courses,
    max_candidates=30
)

# ============================================================
# FEASIBILITY FILTER
# ============================================================

DIGITAL_LEVEL_ORDER = {
    "low": 1,
    "medium": 2,
    "high": 3
}


def check_feasibility(profile, course):

    reasons = []

    # --------------------------------------------------------
    # Course availability
    # --------------------------------------------------------

    if course["course_status"] != "open":
        reasons.append("Course is not open.")

    if course["available_places"] <= 0:
        reasons.append("No available places.")

    # --------------------------------------------------------
    # Language
    # --------------------------------------------------------

    if (
        str(course["language"]).lower()
        != str(profile.preferred_language).lower()
    ):
        reasons.append(
            "Language does not match preferred language."
        )

    # --------------------------------------------------------
    # Delivery mode
    # --------------------------------------------------------

    user_delivery = str(
        profile.delivery_preference
    ).lower()

    course_delivery = str(
        course["delivery_mode"]
    ).lower()

    if (
        user_delivery == "remote"
        and course_delivery == "in_person"
    ):
        reasons.append(
            "Course is in-person, but user prefers remote."
        )

    if (
        user_delivery == "in_person"
        and course_delivery == "remote"
    ):
        reasons.append(
            "Course is remote, but user prefers in-person."
        )

    # --------------------------------------------------------
    # Availability / workload
    # --------------------------------------------------------

    if (
        str(profile.availability).lower() == "part_time"
        and str(course["workload"]).lower() == "full_time"
    ):
        reasons.append(
            "Course workload is full-time, "
            "but user is available part-time."
        )

    # --------------------------------------------------------
    # Digital readiness
    # --------------------------------------------------------

    user_digital = DIGITAL_LEVEL_ORDER.get(
        str(profile.digital_level).lower(),
        0
    )

    required_digital = DIGITAL_LEVEL_ORDER.get(
        str(course["digital_level_required"]).lower(),
        0
    )

    if user_digital < required_digital:
        reasons.append(
            "Course requires a higher digital level."
        )

    # --------------------------------------------------------
    # Accessibility support
    # --------------------------------------------------------

    support_need = str(
        profile.accessibility_need
    ).lower()

    supports = [
        str(x).lower()
        for x in course["accessibility_supports"]
    ]

    if support_need not in ["none", "", "nan"]:

        if (
            support_need not in supports
            and not course["training_assistant_available"]
        ):
            reasons.append(
                "Required accessibility support "
                "is not available."
            )

    # --------------------------------------------------------
    # Previously completed course
    # --------------------------------------------------------

    previous_courses = [
        str(x).lower()
        for x in profile.previous_courses
    ]

    if str(course["title"]).lower() in previous_courses:
        reasons.append(
            "Course has already been completed."
        )

    return len(reasons) == 0, reasons



# ============================================================
# APPLY FEASIBILITY FILTER
# ============================================================

feasibility_results = []

for _, course in candidate_courses.iterrows():

    feasible, reasons = check_feasibility(
        profile,
        course
    )

    course_record = course.to_dict()

    course_record["feasible"] = feasible
    course_record["infeasible_reasons"] = reasons

    feasibility_results.append(
        course_record
    )


feasibility_results = pd.DataFrame(
    feasibility_results
)


if feasibility_results.empty:

    feasible_courses = pd.DataFrame(
        columns=list(candidate_courses.columns) + [
            "feasible",
            "infeasible_reasons"
        ]
    )

else:

    feasible_courses = (
        feasibility_results[
            feasibility_results["feasible"] == True
        ]
        .copy()
        .reset_index(drop=True)
    )


# ============================================================
# RANKING / MATCHING
# ============================================================

RANKING_WEIGHTS = {
    "target_role_fit": 0.30,
    "skill_fit": 0.25,
    "digital_fit": 0.15,
    "green_fit": 0.10,
    "labour_market_fit": 0.20
}


def calculate_target_role_fit(profile, course):

    if (
        str(profile.target_role).lower()
        == str(course["target_role"]).lower()
    ):
        return 100.0

    return 0.0


def calculate_skill_fit(profile, course):

    user_skills = {
        str(skill).lower()
        for skill in profile.skills
    }

    course_skills = {
        str(skill).lower()
        for skill in course["skills_taught"]
    }

    if len(course_skills) == 0:
        return 0.0, [], []

    existing_overlap = (
        user_skills.intersection(
            course_skills
        )
    )

    new_skills = (
        course_skills
        - user_skills
    )

    overlap_ratio = (
        len(existing_overlap)
        / len(course_skills)
    )

    new_skill_ratio = (
        len(new_skills)
        / len(course_skills)
    )

    score = (
        overlap_ratio * 40
        +
        new_skill_ratio * 60
    )

    return (
        round(score, 1),
        sorted(existing_overlap),
        sorted(new_skills)
    )


def calculate_digital_fit(profile, course):

    user_level = DIGITAL_LEVEL_ORDER.get(
        str(profile.digital_level).lower(),
        0
    )

    required_level = DIGITAL_LEVEL_ORDER.get(
        str(
            course["digital_level_required"]
        ).lower(),
        0
    )

    if user_level == required_level:
        return 100.0

    elif user_level == required_level + 1:
        return 80.0

    elif user_level >= required_level + 2:
        return 60.0

    return 0.0


def calculate_green_fit(profile, course):

    green_relevance = str(
        course["green_relevance"]
    ).lower()

    # TEMPORARY PROTOTYPE LOGIC
    if profile.green_class == 1:

        score_map = {
            "low": 30,
            "medium": 70,
            "high": 100
        }

    else:

        score_map = {
            "low": 60,
            "medium": 80,
            "high": 90
        }

    return float(
        score_map.get(
            green_relevance,
            50
        )
    )


def calculate_labour_market_fit(
    course,
    labour_market
):

    role_data = labour_market[
        labour_market["target_role"]
        == course["target_role"]
    ]

    if len(role_data) == 0:
        return 50.0

    course_skills = {
        str(skill).lower()
        for skill in course["skills_taught"]
    }

    relevant = role_data[
        role_data["skill"]
        .str.lower()
        .isin(course_skills)
    ]

    if len(relevant) == 0:
        return 50.0

    return round(
        float(
            relevant[
                "labour_market_score"
            ].mean()
        ),
        1
    )


def rank_courses(
    profile,
    feasible_courses,
    labour_market
):

    ranked_records = []

    for _, course in feasible_courses.iterrows():

        target_score = (
            calculate_target_role_fit(
                profile,
                course
            )
        )

        (
            skill_score,
            existing_skills,
            new_skills
        ) = calculate_skill_fit(
            profile,
            course
        )

        digital_score = (
            calculate_digital_fit(
                profile,
                course
            )
        )

        green_score = (
            calculate_green_fit(
                profile,
                course
            )
        )

        labour_score = (
            calculate_labour_market_fit(
                course,
                labour_market
            )
        )

        final_score = (
            target_score
            * RANKING_WEIGHTS[
                "target_role_fit"
            ]
            +
            skill_score
            * RANKING_WEIGHTS[
                "skill_fit"
            ]
            +
            digital_score
            * RANKING_WEIGHTS[
                "digital_fit"
            ]
            +
            green_score
            * RANKING_WEIGHTS[
                "green_fit"
            ]
            +
            labour_score
            * RANKING_WEIGHTS[
                "labour_market_fit"
            ]
        )

        record = course.to_dict()

        record["target_role_score"] = (
            round(target_score, 1)
        )

        record["skill_score"] = (
            round(skill_score, 1)
        )

        record["digital_score"] = (
            round(digital_score, 1)
        )

        record["green_score"] = (
            round(green_score, 1)
        )

        record["labour_market_score"] = (
            round(labour_score, 1)
        )

        record["existing_skill_overlap"] = (
            existing_skills
        )

        record["new_skills_taught"] = (
            new_skills
        )

        record["final_match_score"] = (
            round(final_score, 1)
        )

        ranked_records.append(
            record
        )

    ranked = pd.DataFrame(
        ranked_records
    )

    if ranked.empty:
        return ranked

    ranked = (
        ranked
        .sort_values(
            "final_match_score",
            ascending=False
        )
        .reset_index(drop=True)
    )

    ranked["rank"] = range(
        1,
        len(ranked) + 1
    )

    return ranked

ranked_courses = rank_courses(
    profile=profile,
    feasible_courses=feasible_courses,
    labour_market=labour_market
)

top_recommendations = (
    ranked_courses
    .head(5)
    .copy()
)

# ============================================================
# CREATE USER-FACING EXPLANATIONS
# ============================================================

def create_match_label(score):

    if score >= 85:
        return "Very strong match"

    elif score >= 70:
        return "Strong match"

    elif score >= 55:
        return "Good match"

    else:
        return "Possible match"


def create_recommendation_explanation(
    profile,
    course
):

    reasons = []
    tradeoffs = []

    # --------------------------------------------------------
    # Target role
    # --------------------------------------------------------

    if course["target_role_score"] == 100:

        reasons.append(
            f"Directly supports your target role: "
            f"{profile.target_role}."
        )

    else:

        tradeoffs.append(
            "The course does not directly match "
            "your stated target role."
        )

    # --------------------------------------------------------
    # New skills
    # --------------------------------------------------------

    if len(
        course["new_skills_taught"]
    ) > 0:

        reasons.append(
            "Develops new skills: "
            + ", ".join(
                course[
                    "new_skills_taught"
                ]
            )
            + "."
        )

    # --------------------------------------------------------
    # Existing skills
    # --------------------------------------------------------

    if len(
        course[
            "existing_skill_overlap"
        ]
    ) > 0:

        reasons.append(
            "Builds on skills you already have: "
            + ", ".join(
                course[
                    "existing_skill_overlap"
                ]
            )
            + "."
        )

    # --------------------------------------------------------
    # Digital fit
    # --------------------------------------------------------

    if course["digital_score"] >= 80:

        reasons.append(
            "The course level is well aligned "
            "with your current digital profile."
        )

    elif course["digital_score"] < 80:

        tradeoffs.append(
            "The course may be below your current "
            "digital capability."
        )

    # --------------------------------------------------------
    # Labour-market relevance
    # --------------------------------------------------------

    if course[
        "labour_market_score"
    ] >= 70:

        reasons.append(
            "The skills taught show strong "
            "simulated labour-market demand."
        )

    elif course[
        "labour_market_score"
    ] < 50:

        tradeoffs.append(
            "Simulated labour-market demand for "
            "the taught skills is comparatively weaker."
        )

    return reasons, tradeoffs

# ============================================================
# APPLY EXPLANATIONS TO TOP RECOMMENDATIONS
# ============================================================

if not top_recommendations.empty:

    explanation_results = (
        top_recommendations.apply(
            lambda row:
                create_recommendation_explanation(
                    profile,
                    row
                ),
            axis=1
        )
    )

    top_recommendations[
        "reasons_for_fit"
    ] = [
        result[0]
        for result in explanation_results
    ]

    top_recommendations[
        "tradeoffs"
    ] = [
        result[1]
        for result in explanation_results
    ]

    top_recommendations[
        "match_label"
    ] = (
        top_recommendations[
            "final_match_score"
        ]
        .apply(
            create_match_label
        )
    )

# ============================================================
# USER-FACING RECOMMENDATION OUTPUT
# ============================================================

jobseeker_output = (
    top_recommendations
    .copy()
)

has_recommendations = not jobseeker_output.empty

    
# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:

    st.image(
        "diamond_logo.png",
        use_container_width=True
    )

    st.caption(
        "Shaping Potentials · Sparking Success"
    )

    st.divider()

    st.subheader("Your ᴱGROW profile")

    st.write(f"**User:** {user_id}")

    st.write(f"**Digital profile:** {digital_profile}")
    st.write(f"**Green profile:** {green_profile}")
    st.write(f"**Target role:** {target_role}")
    st.write(f"**Preferred language:** {preferred_language}")
    st.write(f"**Delivery preference:** {delivery_preference}")

    st.divider()

    st.subheader("Navigation")

    st.write("🏠 MOVEᴱ dashboard")
    st.write("📚 My learning")
    st.write("⭐ Recommended learning")
    st.write("💎 My ᴱGROW profile")

    st.divider()

    st.subheader("Courses I'm interested in")

    if st.session_state.interested_courses:

        interested_rows = courses[
            courses["course_id"].isin(
                st.session_state.interested_courses
            )
        ]

        for _, course in interested_rows.iterrows():
            st.write(f"✓ {course['title']}")

    else:
        st.caption(
            "Courses you mark as interesting will appear here."
        )



# ============================================================
# COURSE CATALOGUE PAGE
# ============================================================

if page_mode == "Course catalogue":

    st.markdown(
        '<div class="diamond-kicker">DIAMOND · MOVEᴱ</div>',
        unsafe_allow_html=True
    )

    st.title("Course catalogue")

    st.write(
        "Explore all simulated learning opportunities in the MOVEᴱ prototype. "
        "The catalogue is not limited to the courses recommended for the selected jobseeker."
    )

    st.caption(
        f"{len(courses)} simulated courses available"
    )

    st.divider()

    # --------------------------------------------------------
    # Catalogue filters
    # --------------------------------------------------------

    search_text = st.text_input(
        "Search courses",
        placeholder="Search by title, provider, role or skill"
    )

    col1, col2, col3 = st.columns(3)

    with col1:
        delivery_filter = st.selectbox(
            "Delivery",
            options=["All"] + sorted(
                courses["delivery_mode"]
                .dropna()
                .astype(str)
                .unique()
                .tolist()
            )
        )

    with col2:
        language_filter = st.selectbox(
            "Language",
            options=["All"] + sorted(
                courses["language"]
                .dropna()
                .astype(str)
                .unique()
                .tolist()
            )
        )

    with col3:
        level_filter = st.selectbox(
            "Digital level",
            options=["All", "low", "medium", "high"]
        )

    catalogue = courses.copy()

    if search_text.strip():

        query = search_text.strip().lower()

        def catalogue_match(row):
            searchable = [
                str(row.get("title", "")),
                str(row.get("provider", "")),
                str(row.get("target_role", "")),
                " ".join(
                    str(x)
                    for x in row.get("skills_taught", [])
                )
                if isinstance(row.get("skills_taught", []), list)
                else str(row.get("skills_taught", ""))
            ]

            return query in " ".join(searchable).lower()

        catalogue = catalogue[
            catalogue.apply(
                catalogue_match,
                axis=1
            )
        ]

    if delivery_filter != "All":
        catalogue = catalogue[
            catalogue["delivery_mode"].astype(str)
            == delivery_filter
        ]

    if language_filter != "All":
        catalogue = catalogue[
            catalogue["language"].astype(str)
            == language_filter
        ]

    if level_filter != "All":
        catalogue = catalogue[
            catalogue["digital_level_required"].astype(str)
            == level_filter
        ]

    st.write(
        f"**{len(catalogue)} course(s) match the current filters.**"
    )

    if catalogue.empty:
        st.info(
            "No courses match the current catalogue filters."
        )
        st.stop()

    # --------------------------------------------------------
    # Select any simulated course
    # --------------------------------------------------------

    course_label_map = {
        row["course_id"]:
            f"{row['title']} · {row['provider']} · {row['course_id']}"
        for _, row in catalogue.iterrows()
    }

    selected_catalogue_course_id = st.selectbox(
        "Select a course",
        options=catalogue["course_id"].tolist(),
        format_func=lambda course_id:
            course_label_map.get(
                course_id,
                course_id
            )
    )

    catalogue_course = catalogue[
        catalogue["course_id"]
        == selected_catalogue_course_id
    ].iloc[0]

    feasible_for_user, catalogue_feasibility_reasons = (
        check_feasibility(
            profile,
            catalogue_course
        )
    )

    target_score = calculate_target_role_fit(
        profile,
        catalogue_course
    )

    (
        catalogue_skill_score,
        catalogue_existing_skills,
        catalogue_new_skills
    ) = calculate_skill_fit(
        profile,
        catalogue_course
    )

    catalogue_digital_score = calculate_digital_fit(
        profile,
        catalogue_course
    )

    catalogue_green_score = calculate_green_fit(
        profile,
        catalogue_course
    )

    catalogue_labour_score = calculate_labour_market_fit(
        catalogue_course,
        labour_market
    )

    catalogue_match_score = round(
        target_score * RANKING_WEIGHTS["target_role_fit"]
        + catalogue_skill_score * RANKING_WEIGHTS["skill_fit"]
        + catalogue_digital_score * RANKING_WEIGHTS["digital_fit"]
        + catalogue_green_score * RANKING_WEIGHTS["green_fit"]
        + catalogue_labour_score * RANKING_WEIGHTS["labour_market_fit"],
        1
    )

    st.divider()

    st.subheader(
        catalogue_course["title"]
    )

    st.write(
        f"**Provider:** {catalogue_course['provider']}"
    )

    if feasible_for_user:
        st.success(
            f"Feasible for {profile.user_id} · "
            f"Indicative match {catalogue_match_score}/100"
        )
    else:
        st.warning(
            f"Not currently feasible for {profile.user_id} · "
            f"Indicative match {catalogue_match_score}/100"
        )

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            "Delivery",
            catalogue_course["delivery_mode"]
        )

    with col2:
        st.metric(
            "Language",
            catalogue_course["language"]
        )

    with col3:
        st.metric(
            "Duration",
            f"{catalogue_course['duration_weeks']} weeks"
        )

    with col4:
        st.metric(
            "Digital level",
            catalogue_course["digital_level_required"]
        )

    st.write(
        f"**Target role:** {catalogue_course['target_role']}"
    )

    st.write("**Skills taught**")

    for skill in catalogue_course["skills_taught"]:
        st.write(f"• {skill}")

    if catalogue_course["micro_credentials"]:
        st.write("**Micro-credentials**")
        for credential in catalogue_course["micro_credentials"]:
            st.write(f"• {credential}")

    st.write("**Course availability**")
    st.write(
        f"Status: {catalogue_course['course_status']} · "
        f"Available places: {catalogue_course['available_places']}"
    )

    if not feasible_for_user:
        st.write("**Why this course is not currently feasible**")
        for reason in catalogue_feasibility_reasons:
            st.write(f"• {reason}")

    st.divider()

    if (
        catalogue_course["course_id"]
        in st.session_state.interested_courses
    ):
        st.success(
            "✓ You have marked this course as interesting."
        )
    else:
        if st.button(
            "I'm interested in this course",
            key=f"catalogue_interest_{catalogue_course['course_id']}",
            type="primary"
        ):
            mark_interested(
                catalogue_course["course_id"]
            )
            st.rerun()

    st.caption(
        "Catalogue selections are exploratory. "
        "Only feasible courses can enter the recommendation ranking."
    )

    st.stop()


# ============================================================
# EGROW PROFILE PAGE
# ============================================================

if page_mode == "My ᴱGROW profile":

    st.markdown(
        '<div class="diamond-kicker">DIAMOND · ᴱGROW</div>',
        unsafe_allow_html=True
    )

    st.title("My ᴱGROW profile")

    st.write(
        "This simulated profile is the user representation "
        "used by the Version 2 recommendation pipeline."
    )

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Capability profile")
        st.write(
            f"**Digital profile:** {profile.digital_profile}"
        )
        st.write(
            f"**Digital level:** {profile.digital_level}"
        )
        st.write(
            f"**Green profile:** {profile.green_profile}"
        )
        st.write(
            f"**Profile confidence:** {profile.profile_confidence}"
        )

    with col2:
        st.subheader("Learning and career context")
        st.write(
            f"**Target role:** {profile.target_role}"
        )
        st.write(
            f"**Preferred language:** {profile.preferred_language}"
        )
        st.write(
            f"**Delivery preference:** {profile.delivery_preference}"
        )
        st.write(
            f"**Availability:** {profile.availability}"
        )

    st.subheader("Current skills")

    for skill in profile.skills:
        st.write(f"• {skill}")

    st.subheader("Previous courses")

    if profile.previous_courses:
        for course in profile.previous_courses:
            st.write(f"• {course}")
    else:
        st.write("No previous courses recorded.")

    st.stop()


# ============================================================
# COURSE DETAIL PAGE
# ============================================================

if (
    page_mode == "Recommended learning"
    and st.session_state.viewed_course is not None
):

    detail = jobseeker_output[
        jobseeker_output["course_id"]
        == st.session_state.viewed_course
    ].iloc[0]

    if st.button("← Back to recommended learning"):
        close_course()
        st.rerun()

    st.title(detail["title"])

    st.write(f"**Provider:** {detail['provider']}")

    st.success(
        f"{detail['match_label']} · "
        f"{detail['final_match_score']}/100"
    )

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            "Match score",
            f"{detail['final_match_score']}/100"
        )

    with col2:
        st.metric(
            "Duration",
            f"{detail['duration_weeks']} weeks"
        )

    with col3:
        st.metric(
            "Delivery",
            detail["delivery_mode"]
        )

    with col4:
        st.metric(
            "Language",
            detail["language"]
        )

    st.divider()

    st.subheader("Why this course may fit you")

    for reason in detail["reasons_for_fit"]:
        st.write(f"✓ {reason}")

    st.subheader("Skills you may develop")

    for skill in detail["skills_taught"]:
        st.write(f"• {skill}")

    if len(detail["micro_credentials"]) > 0:

        st.subheader("Micro-credentials")

        for credential in detail["micro_credentials"]:
            st.write(f"• {credential}")

    st.subheader("Things to consider")

    if len(detail["tradeoffs"]) > 0:

        for tradeoff in detail["tradeoffs"]:
            st.write(f"• {tradeoff}")

    else:

        st.write(
            "No major trade-offs identified."
        )

    st.divider()

    if (
        detail["course_id"]
        in st.session_state.interested_courses
    ):

        st.success(
            "✓ You have marked this course as interesting."
        )

    else:

        if st.button(
            "I'm interested",
            key=f"detail_interest_{detail['course_id']}",
            type="primary"
        ):

            mark_interested(
                detail["course_id"]
            )

            st.rerun()

    st.stop()


# ============================================================
# RECOMMENDATION FALLBACK
# ============================================================

if (
    page_mode == "Recommended learning"
    and not has_recommendations
):

    st.markdown(
        '<div class="diamond-kicker">DIAMOND · MOVEᴱ</div>',
        unsafe_allow_html=True
    )

    st.title("Your personalised learning pathway")

    st.warning(
        "No feasible course recommendations were found "
        "for this simulated jobseeker."
    )

    st.write(
        "You can still explore the complete simulated course catalogue "
        "from the sidebar. Courses that do not currently pass the "
        "feasibility filter will be shown with the reasons why."
    )

    if not feasibility_results.empty:

        reason_counts = {}

        for reasons in feasibility_results[
            "infeasible_reasons"
        ]:
            for reason in reasons:
                reason_counts[reason] = (
                    reason_counts.get(
                        reason,
                        0
                    ) + 1
                )

        if reason_counts:

            st.subheader(
                "Most common feasibility barriers"
            )

            for reason, count in sorted(
                reason_counts.items(),
                key=lambda item: item[1],
                reverse=True
            )[:5]:

                st.write(
                    f"• {reason} ({count} course(s))"
                )

    st.stop()


# ============================================================
# MAIN PAGE
# ============================================================

st.markdown(
    '<div class="diamond-kicker">DIAMOND · MOVEᴱ</div>',
    unsafe_allow_html=True
)

st.title("Your personalised learning pathway")

st.markdown(
    '<div class="diamond-subtitle">'
    'MOVEᴱ uses your ᴱGROW profile and simulated labour-market insights '
    'to identify learning opportunities that may support your employability growth.'
    '</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="prototype-note">'
    '<strong>Prototype demonstration:</strong> This version uses synthetic '
    'jobseeker, course and labour-market data.'
    '</div>',
    unsafe_allow_html=True
)

st.divider()

st.header("Recommended learning opportunities")

st.write(
    "These recommendations are generated from your simulated ᴱGROW profile, "
    "career direction, existing skills, learning preferences and feasibility constraints."
)

st.caption(
    f"Simulated participant: {user_id}"
)

st.write("")


# ============================================================
# COURSE CARDS
# ============================================================

for _, row in (
    jobseeker_output
    .sort_values("rank")
    .iterrows()
):

    with st.container(border=True):

        st.caption(
            f"Recommendation #{int(row['rank'])}"
        )

        st.subheader(
            row["title"]
        )

        st.write(
            f"**Provider:** {row['provider']}"
        )

        st.success(
            f"{row['match_label']} · "
            f"{row['final_match_score']}/100"
        )

        col1, col2, col3 = st.columns(3)

        with col1:
            st.write(
                f"**Delivery**  \n"
                f"{row['delivery_mode']}"
            )

        with col2:
            st.write(
                f"**Language**  \n"
                f"{row['language']}"
            )

        with col3:
            st.write(
                f"**Duration**  \n"
                f"{row['duration_weeks']} weeks"
            )

        st.write("**Why this course may fit you**")

        for reason in row["reasons_for_fit"]:
            st.write(f"✓ {reason}")

        st.write("**Skills you may develop**")

        skills_text = " · ".join(
            row["skills_taught"]
        )

        st.write(skills_text)

        st.write("**Things to consider**")

        if len(row["tradeoffs"]) > 0:

            for tradeoff in row["tradeoffs"]:
                st.write(f"• {tradeoff}")

        else:

            st.write(
                "No major trade-offs identified."
            )

        col1, col2, col3 = st.columns(
            [1, 1, 2]
        )

        with col1:

            if st.button(
                "View course",
                key=f"view_{row['course_id']}"
            ):

                open_course(
                    row["course_id"]
                )

                st.rerun()

        with col2:

            if (
                row["course_id"]
                in st.session_state.interested_courses
            ):

                st.success("✓ Interested")

            else:

                if st.button(
                    "I'm interested",
                    key=f"interest_{row['course_id']}",
                    type="primary"
                ):

                    mark_interested(
                        row["course_id"]
                    )

                    st.rerun()


# ============================================================
# SELECTED INTERESTS
# ============================================================

if st.session_state.interested_courses:

    st.divider()

    st.subheader("Learning opportunities you are interested in")

    selected = jobseeker_output[
        jobseeker_output["course_id"].isin(
            st.session_state.interested_courses
        )
    ]

    for _, course in selected.iterrows():

        st.write(
            f"✓ **{course['title']}**"
        )

    st.info(
        "In the full DIAMOND recommender workflow, these selections "
        "would feed into the feedback loop and future learning recommendations."
    )


# ============================================================
# FOOTER
# ============================================================

st.divider()

st.caption(
    "EGROW recommender system prototype — "
    "synthetic data only."
)
