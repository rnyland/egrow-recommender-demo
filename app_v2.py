import streamlit as st
import pandas as pd


# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="EGROW Learning Platform",
    page_icon="🎓",
    layout="wide"
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

if jobseeker_output.empty:

    st.warning(
        "No feasible course recommendations were found "
        "for this simulated jobseeker."
    )

    st.stop()

    
# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:

    st.title("EGROW")

    st.subheader("My profile")

    st.write(f"**User:** {user_id}")

    st.write(f"**Digital profile:** {digital_profile}")
    st.write(f"**Green profile:** {green_profile}")
    st.write(f"**Target role:** {target_role}")
    st.write(f"**Preferred language:** {preferred_language}")
    st.write(f"**Delivery preference:** {delivery_preference}")

    st.divider()

    st.subheader("Navigation")

    st.write("🏠 Dashboard")
    st.write("📚 My courses")
    st.write("⭐ Recommended courses")
    st.write("👤 Profile")

    st.divider()

    st.subheader("Courses I'm interested in")

    if st.session_state.interested_courses:

        interested_rows = jobseeker_output[
            jobseeker_output["course_id"].isin(
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
# COURSE DETAIL PAGE
# ============================================================

if st.session_state.viewed_course is not None:

    detail = jobseeker_output[
        jobseeker_output["course_id"]
        == st.session_state.viewed_course
    ].iloc[0]

    if st.button("← Back to recommendations"):
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
# MAIN PAGE
# ============================================================

st.title("EGROW Learning Platform")

st.caption(
    "My dashboard › Course recommendations"
)

st.divider()

st.header("Recommended courses for you")

st.write(
    "These recommendations are based on your current "
    "profile, career goals, skills and training preferences."
)

st.caption(
    f"Demo user: {user_id}"
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

    st.subheader("Your selected interests")

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
        "In the full EGROW system, these selections "
        "would be sent back to the feedback loop."
    )


# ============================================================
# FOOTER
# ============================================================

st.divider()

st.caption(
    "EGROW recommender system prototype — "
    "synthetic data only."
)
