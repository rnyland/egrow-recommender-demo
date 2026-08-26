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

    return (
        jobseekers,
        courses
    )


jobseekers, courses = load_data()

# ============================================================
# DEMO ROLE + SELECT JOBSEEKER
# ============================================================

# Purpose: Selects whether the prototype is viewed as a caseworker 
# or applicant and selects the applicant whose data are used.

# Create the switch option in the sidebar to choose which version to see.
# * Caseworker    --> Professional view (default selection)
# * Jobseeker     --> Applicant view

demo_role = st.sidebar.radio(
    "Demo as",
    options=[
        "Caseworker",
        "Jobseeker"
    ],
    index=0
)

# Make a list of all simulated applicants from the applicant list and collect their user IDs.
# Feed the list to dropdown menu.

user_options = (
    jobseekers["user_id"]
    .sort_values()
    .tolist()
)

# Change the label depending on the selected view.

user_selector_label = (
    "Select jobseeker to review"
    if demo_role == "Caseworker"
    else "Simulated login"
)

# Make it possible to select an applicant.
# Define the selected applicant.

selected_user_id = st.sidebar.selectbox(
    user_selector_label,
    options=user_options
)

# Retrieve the applicant's data.
# e.g., EGROW profile and learning preferences.

selected_user = (
    jobseekers[
        jobseekers["user_id"] == selected_user_id
    ]
    .iloc[0]
)

# ============================================================
# SESSION STATE
# ============================================================

# Session State: Temporarily remembers user interactions and 
# caseworker decisions while the prototype is being used.

# Stores courses the applicant signs up for.
if "signed_up_courses" not in st.session_state:
    st.session_state.signed_up_courses = []

# Remembers which courses the user is currently viewing.
if "viewed_course" not in st.session_state:
    st.session_state.viewed_course = None

# Stores the saseworker's approved courses for each applicant.
if "approvals_by_user" not in st.session_state:
    st.session_state.approvals_by_user = {}

# Creates an empty approval list for a newly selected applicant.
if selected_user_id not in st.session_state.approvals_by_user:
    st.session_state.approvals_by_user[selected_user_id] = []

# Keeps track of which simulated jobseeker is currently selected.
if "active_user_id" not in st.session_state:
    st.session_state.active_user_id = selected_user_id

# Resets the interface when switching to another applicant. 
elif st.session_state.active_user_id != selected_user_id:
    st.session_state.active_user_id = selected_user_id
    st.session_state.signed_up_courses = []
    st.session_state.viewed_course = None


# ============================================================
# HELPER FUNCTIONS
# ============================================================

# Signs the applicant up for a selected course.
def sign_up_for_course(course_id):
    if course_id not in st.session_state.signed_up_courses:
        st.session_state.signed_up_courses.append(course_id)

# Opens a selected course.
def open_course(course_id):
    st.session_state.viewed_course = course_id

# Closes the selected course.
def close_course():
    st.session_state.viewed_course = None

# Approves a course for a specific applicant. 
def approve_course(user_id, course_id):
    approved = st.session_state.approvals_by_user.setdefault(
        user_id,
        []
    )

    if course_id not in approved:
        approved.append(course_id)

# Removes a caseworker's course approval.
def remove_course_approval(user_id, course_id):
    approved = st.session_state.approvals_by_user.setdefault(
        user_id,
        []
    )

    if course_id in approved:
        approved.remove(course_id)

# Removes all course approvals for a specific applicant.
def clear_user_approvals(user_id):
    st.session_state.approvals_by_user[user_id] = []


# ============================================================
# USER SELECTION
# ============================================================

# Purpose: Retrieves the selected applicant's key profile information.

# Identify the currently selected applicant.
user_id = selected_user_id

# Basic selected-user information
digital_profile = selected_user["digital_profile"]
green_profile = selected_user["green_profile"]
preferred_language = selected_user["preferred_language"]
delivery_preference = selected_user["delivery_preference"] 

# ============================================================
# PROFILE EXTRACTION
# ============================================================

# Purpose: Builds and checks a structured profile for the selected applicant.

from dataclasses import dataclass, field
from typing import Optional

# Defines which information is stored in a jobseeker profile.

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

# Defines the information required before recommendations can be made.

CRITICAL_PROFILE_FIELDS = [
    "digital_profile",
    "green_profile",
    "preferred_language",
    "delivery_preference"
]


def extract_jobseeker_profile(user):

    # Checks whether required profile information is missing.
    
    missing_fields = []

    for field_name in CRITICAL_PROFILE_FIELDS:

        value = user.get(field_name, None)

        if (
            value is None
            or pd.isna(value)
            or value == ""
        ):
            missing_fields.append(field_name)

    # Checks for conflicting information from different data sources.
    
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

    # Assesses how reliable and complete the applicant's profile is.
    
    if len(missing_fields) == 0 and len(conflicts) == 0:
        profile_confidence = "high"

    elif len(missing_fields) <= 1 and len(conflicts) <= 1:
        profile_confidence = "medium"

    else:
        profile_confidence = "low"

    # Identifies issues that prevent the system from making recommendations.
    
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

    # Determines whether the profile is ready for recommendations.
    
    can_recommend = len(blockers) == 0

    # Combines all available applicant information into one structured profile.
    
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

# Creates the profile for the currently selected jobseeker.

profile = extract_jobseeker_profile(
    selected_user
)


# ============================================================
# COURSE RETRIEVAL
# ============================================================

# Purpose: Selects the initial pool of courses to be considered by the recommender.

# Selects up to 30 courses from the full course catalogue.

def retrieve_candidate_courses(courses):

    # Consider all available courses.

    candidate_courses = (courses.copy())

    return candidate_courses

# Retrieves the full course catalogue for further assessment.

candidate_courses = retrieve_candidate_courses(
    courses=courses
)


# ============================================================
# FEASIBILITY FILTER
# ============================================================

# Purpose: Removes courses that are not practically suitable for the applicant.

# Defines the order of digital capability levels.

DIGITAL_LEVEL_ORDER = {
    "low": 1,
    "medium": 2,
    "high": 3
}

# Checks whether each course is feasible for the selected applicant.

def check_feasibility(profile, course):

    reasons = []

    # --------------------------------------------------------
    # Course availability
    # --------------------------------------------------------

    # Checks whether the course is open and has available places.
    
    if course["course_status"] != "open":
        reasons.append("Course is not open.")

    if course["available_places"] <= 0:
        reasons.append("No available places.")

    # --------------------------------------------------------
    # Delivery mode
    # --------------------------------------------------------

    # Checks whether the delivery mode matches the applicant's preference.
    
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
    # Digital readiness
    # --------------------------------------------------------

    # Checks whether the jobseeker has the digital level required for the course.
    
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

    # Checks whether required accessibility support is available.
    
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

    # Excludes courses the jobseeker has already completed.
    
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

# Purpose: Applies the feasibility checks to all candidate courses and keeps only the feasible ones.

# Creates an empty list to store the feasibility results.

feasibility_results = []

# Checks every candidate course against the feasibility rules.

for _, course in candidate_courses.iterrows():
    
    # Records whether the course is feasible and why it may be excluded.
    
    feasible, reasons = check_feasibility(
        profile,
        course
    )

    # Adds the feasibility result to the course information.
    
    course_record = course.to_dict()

    course_record["feasible"] = feasible
    course_record["infeasible_reasons"] = reasons

    # Stores the result for later use.
    
    feasibility_results.append(
        course_record
    )

# Converts all feasibility results into a dataframe.

feasibility_results = pd.DataFrame(
    feasibility_results
)

# Creates an empty result if no courses were assessed.

if feasibility_results.empty:

    feasible_courses = pd.DataFrame(
        columns=list(candidate_courses.columns) + [
            "feasible",
            "infeasible_reasons"
        ]
    )
    
# Keeps only courses that passed all feasibility checks.

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

# Purpose: Scores and ranks feasible courses based on digital and green fit.

# Sets how much digital and green fit contribute to the final score.

RANKING_WEIGHTS = {
    "digital_fit": 0.50,
    "green_fit": 0.50
}

# Calculates how well the course's digital level matches the jobseeker.

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

    # Gives a higher score when the course level closely matches the user's digital level.
    
    if user_level == required_level:
        return 100.0

    elif user_level == required_level + 1:
        return 80.0

    elif user_level >= required_level + 2:
        return 60.0

    return 0.0

# Calculates how well the course's green relevance matches the jobseeker's green profile.

def calculate_green_fit(profile, course):

    green_relevance = str(
        course["green_relevance"]
    ).lower()

    # Assigns a green-fit score based on the user's green profile class.
    
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

# Calculates a final score for every feasible course.

def rank_courses(
    profile,
    feasible_courses
):

    ranked_records = []

    for _, course in feasible_courses.iterrows():

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

        # Combines digital fit and green fit into one recommendation score.
        
        final_score = (
            digital_score
            * RANKING_WEIGHTS[
                "digital_fit"
            ]
            +
            green_score
            * RANKING_WEIGHTS[
                "green_fit"
            ]
        )

        record = course.to_dict()

        record["digital_score"] = (
            round(digital_score, 1)
        )

        record["green_score"] = (
            round(green_score, 1)
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

    # Sorts courses from highest to lowest match score.
    
    ranked = (
        ranked
        .sort_values(
            "final_match_score",
            ascending=False
        )
        .reset_index(drop=True)
    )

    # Adds a ranking number to each course.
    
    ranked["rank"] = range(
        1,
        len(ranked) + 1
    )

    return ranked

# Runs the ranking process on all feasible courses.

ranked_courses = rank_courses(
    profile=profile,
    feasible_courses=feasible_courses
)

# Keeps all ranked feasible courses as recommendations.

top_recommendations = (
    ranked_courses
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
    # Green fit
    # --------------------------------------------------------

    if course["green_score"] >= 80:

        reasons.append(
            "The course has a strong alignment "
            "with your current green profile."
        )

    elif course["green_score"] < 60:

        tradeoffs.append(
            "The course has a comparatively weaker "
            "alignment with your current green profile."
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
# ============================================================
# ROLE-AWARE SIDEBAR
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

    if demo_role == "Caseworker":

        st.subheader("Caseworker workspace")

        caseworker_page = st.radio(
            "Navigation",
            options=[
                "Review recommendations",
                "Course catalogue"
            ],
            index=0
        )

        st.divider()

        st.subheader("Selected jobseeker")

        st.write(f"**User:** {profile.user_id}")
        st.write(f"**Digital profile:** {profile.digital_profile}")
        st.write(f"**Green profile:** {profile.green_profile}")
        st.write(f"**Language:** {profile.preferred_language}")
        st.write(f"**Delivery:** {profile.delivery_preference}")

        approved_ids_sidebar = (
            st.session_state.approvals_by_user.get(
                profile.user_id,
                []
            )
        )

        st.metric(
            "Approved courses",
            len(approved_ids_sidebar)
        )

    else:

        st.subheader("MOVEᴱ")

        st.write("⭐ Recommended learning")

        st.caption(
            "Only caseworker-approved recommendations "
            "are visible in this jobseeker view."
        )
        
        if st.session_state.signed_up_courses:

            st.divider()

            st.subheader("My course sign-ups")

            signed_up_rows = courses[
                courses["course_id"].isin(
                    st.session_state.signed_up_courses
                )
            ]

            for _, course in signed_up_rows.iterrows():
                st.write(f"✓ {course['title']}")

# ============================================================
# CASEWORKER VIEW
# ============================================================

if demo_role == "Caseworker":

    st.markdown(
        '<div class="diamond-kicker">DIAMOND · CASEWORKER</div>',
        unsafe_allow_html=True
    )

    # --------------------------------------------------------
    # CASEWORKER: REVIEW RECOMMENDATIONS
    # --------------------------------------------------------

    if caseworker_page == "Review recommendations":

        st.title("Review recommended learning")

        st.write(
            "The system has already extracted the jobseeker profile, "
            "retrieved relevant courses, applied the deterministic "
            "feasibility filter, and ranked the remaining options. "
            "The caseworker decides which recommendations may be "
            "shown to the jobseeker."
        )

        st.markdown(
            '<div class="prototype-note">'
            '<strong>Human-in-the-loop:</strong> '
            'Only courses approved here become visible '
            'in the jobseeker view.'
            '</div>',
            unsafe_allow_html=True
        )

        st.subheader("Jobseeker profile")

        col1, col2, col3 = st.columns(3)

        with col1:
            st.write(f"**User:** {profile.user_id}")
            st.write(f"**Employment:** {profile.employment_status}")

        with col2:
            st.write(f"**Digital:** {profile.digital_profile}")
            st.write(f"**Green:** {profile.green_profile}")
            st.write(f"**Language:** {profile.preferred_language}")

        with col3:
            st.write(f"**Delivery:** {profile.delivery_preference}")
            st.write(f"**Availability:** {profile.availability}")
            st.write(f"**Confidence:** {profile.profile_confidence}")

        with st.expander("View additional profile information"):

            st.write(f"**Education:** {profile.education_level}")
            st.write(f"**Location:** {profile.city}, {profile.country}")

            st.write(
                "**Work history:** "
                + (
                    ", ".join(profile.work_history)
                    if profile.work_history
                    else "None recorded"
                )
            )

            st.write(
                "**Previous courses:** "
                + (
                    ", ".join(profile.previous_courses)
                    if profile.previous_courses
                    else "None recorded"
                )
            )

        st.divider()

        if not profile.can_recommend:

            st.error(
                "The profile is not complete enough for recommendations."
            )

            for blocker in profile.recommendation_blockers:
                st.write(f"• {blocker}")

            st.stop()

        if not has_recommendations:

            st.warning(
                "No feasible course recommendations were found "
                "for this jobseeker."
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

            st.info(
                "The full catalogue can still be inspected from "
                "the caseworker navigation, but only feasible ranked "
                "courses can be approved for the jobseeker."
            )

            st.stop()

        action_col1, action_col2, _ = st.columns(
            [1, 1, 2]
        )

        with action_col1:

            if st.button(
                "Approve all",
                type="primary"
            ):

                st.session_state.approvals_by_user[
                    profile.user_id
                ] = (
                    jobseeker_output[
                        "course_id"
                    ]
                    .tolist()
                )

                st.rerun()

        with action_col2:

            if st.button(
                "Clear approvals"
            ):

                clear_user_approvals(
                    profile.user_id
                )

                st.rerun()

        st.caption(
            "Approval status is stored for this browser session "
            "in the prototype."
        )

        st.divider()

        for _, row in (
            jobseeker_output
            .sort_values("rank")
            .iterrows()
        ):

            course_id = row["course_id"]

            approved_ids = (
                st.session_state.approvals_by_user.get(
                    profile.user_id,
                    []
                )
            )

            is_approved = (
                course_id in approved_ids
            )

            with st.container(
                border=True
            ):

                header_col1, header_col2 = st.columns(
                    [4, 1]
                )

                with header_col1:

                    st.caption(
                        f"Recommendation #{int(row['rank'])}"
                    )

                    st.subheader(
                        row["title"]
                    )

                    st.write(
                        f"**Provider:** {row['provider']}"
                    )

                with header_col2:

                    if is_approved:
                        st.success("✓ Approved")
                    else:
                        st.warning("Awaiting review")

                st.write(
                    f"**Match:** {row['match_label']} · "
                    f"{row['final_match_score']}/100"
                )

                meta1, meta2, meta3 = st.columns(3)

                with meta1:
                    st.write(
                        f"**Delivery**  \n"
                        f"{row['delivery_mode']}"
                    )

                with meta2:
                    st.write(
                        f"**Language**  \n"
                        f"{row['language']}"
                    )

                with meta3:
                    st.write(
                        f"**Duration**  \n"
                        f"{row['duration_weeks']} weeks"
                    )

                st.write(
                    "**Why the recommender selected this course**"
                )

                for reason in row[
                    "reasons_for_fit"
                ]:

                    st.write(f"✓ {reason}")

                if row["tradeoffs"]:

                    st.write(
                        "**Trade-offs for caseworker review**"
                    )

                    for tradeoff in row[
                        "tradeoffs"
                    ]:

                        st.write(f"• {tradeoff}")

                st.caption(
                    "This course has already passed the "
                    "deterministic feasibility filter."
                )

                if is_approved:

                    if st.button(
                        "Remove approval",
                        key=(
                            f"remove_approval_"
                            f"{profile.user_id}_"
                            f"{course_id}"
                        )
                    ):

                        remove_course_approval(
                            profile.user_id,
                            course_id
                        )

                        st.rerun()

                else:

                    if st.button(
                        "Approve for jobseeker",
                        key=(
                            f"approve_"
                            f"{profile.user_id}_"
                            f"{course_id}"
                        ),
                        type="primary"
                    ):

                        approve_course(
                            profile.user_id,
                            course_id
                        )

                        st.rerun()

        st.divider()

        approved_ids = (
            st.session_state.approvals_by_user.get(
                profile.user_id,
                []
            )
        )

        st.subheader(
            "Caseworker decision summary"
        )

        if approved_ids:

            approved_summary = jobseeker_output[
                jobseeker_output[
                    "course_id"
                ].isin(
                    approved_ids
                )
            ]

            st.success(
                f"{len(approved_summary)} course(s) approved "
                "for the jobseeker view."
            )

            for _, approved_course in (
                approved_summary
                .sort_values("rank")
                .iterrows()
            ):

                st.write(
                    f"✓ #{int(approved_course['rank'])} "
                    f"{approved_course['title']}"
                )

        else:

            st.info(
                "No courses have been approved yet. "
                "The jobseeker will not see any recommendations."
            )

        st.stop()


    # --------------------------------------------------------
    # CASEWORKER: COURSE CATALOGUE
    # --------------------------------------------------------

    if caseworker_page == "Course catalogue":

        st.title("Course catalogue")

        st.write(
            "The caseworker can inspect all simulated learning "
            "opportunities. Approval remains restricted to courses "
            "that pass feasibility and enter the ranked recommendation set."
        )

        st.caption(
            f"{len(courses)} simulated courses available"
        )

        st.divider()

        search_text = st.text_input(
            "Search courses",
            placeholder=(
                "Search by title or provider"
            )
        )

        col1, col2, col3 = st.columns(3)

        with col1:

            delivery_filter = st.selectbox(
                "Delivery",
                options=["All"] + sorted(
                    courses[
                        "delivery_mode"
                    ]
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
                    courses[
                        "language"
                    ]
                    .dropna()
                    .astype(str)
                    .unique()
                    .tolist()
                )
            )

        with col3:

            level_filter = st.selectbox(
                "Digital level",
                options=[
                    "All",
                    "low",
                    "medium",
                    "high"
                ]
            )

        catalogue = courses.copy()

        if search_text.strip():

            query = (
                search_text
                .strip()
                .lower()
            )

            def catalogue_match(row):

                searchable = " ".join(
                    [
                        str(row.get("title", "")),
                        str(row.get("provider", ""))
                    ]
                ).lower()

                return query in searchable

            catalogue = catalogue[
                catalogue.apply(
                    catalogue_match,
                    axis=1
                )
            ]

        if delivery_filter != "All":

            catalogue = catalogue[
                catalogue[
                    "delivery_mode"
                ].astype(str)
                == delivery_filter
            ]

        if language_filter != "All":

            catalogue = catalogue[
                catalogue[
                    "language"
                ].astype(str)
                == language_filter
            ]

        if level_filter != "All":

            catalogue = catalogue[
                catalogue[
                    "digital_level_required"
                ].astype(str)
                == level_filter
            ]

        st.write(
            f"**{len(catalogue)} course(s) match the current filters.**"
        )

        if catalogue.empty:

            st.info(
                "No courses match the current filters."
            )

            st.stop()

        course_label_map = {
            row["course_id"]:
                f"{row['title']} · "
                f"{row['provider']} · "
                f"{row['course_id']}"
            for _, row in catalogue.iterrows()
        }

        selected_catalogue_course_id = (
            st.selectbox(
                "Select a course",
                options=(
                    catalogue[
                        "course_id"
                    ]
                    .tolist()
                ),
                format_func=lambda course_id:
                    course_label_map.get(
                        course_id,
                        course_id
                    )
            )
        )

        catalogue_course = catalogue[
            catalogue[
                "course_id"
            ]
            == selected_catalogue_course_id
        ].iloc[0]

        (
            feasible_for_user,
            catalogue_feasibility_reasons
        ) = check_feasibility(
            profile,
            catalogue_course
        )

        st.divider()

        st.subheader(
            catalogue_course["title"]
        )

        st.write(
            f"**Provider:** "
            f"{catalogue_course['provider']}"
        )

        if feasible_for_user:

            st.success(
                f"Feasible for {profile.user_id}"
            )

        else:

            st.warning(
                f"Not currently feasible for "
                f"{profile.user_id}"
            )

        meta1, meta2, meta3, meta4 = st.columns(
            4
        )

        with meta1:
            st.metric(
                "Delivery",
                catalogue_course[
                    "delivery_mode"
                ]
            )

        with meta2:
            st.metric(
                "Language",
                catalogue_course[
                    "language"
                ]
            )

        with meta3:
            st.metric(
                "Duration",
                f"{catalogue_course['duration_weeks']} weeks"
            )

        with meta4:
            st.metric(
                "Digital level",
                catalogue_course[
                    "digital_level_required"
                ]
            )

        st.write("**Course availability**")

        st.write(
            f"Status: "
            f"{catalogue_course['course_status']} · "
            f"Available places: "
            f"{catalogue_course['available_places']}"
        )

        if not feasible_for_user:

            st.write(
                "**Why this course is not currently feasible**"
            )

            for reason in (
                catalogue_feasibility_reasons
            ):

                st.write(f"• {reason}")

        ranked_ids = (
            set(
                jobseeker_output[
                    "course_id"
                ]
            )
            if has_recommendations
            else set()
        )

        if (
            catalogue_course[
                "course_id"
            ] in ranked_ids
        ):

            st.info(
                "This course is in the feasible ranked "
                "recommendation set. Approval is managed "
                "from 'Review recommendations'."
            )

        else:

            st.caption(
                "This course is not currently in the feasible "
                "ranked recommendation set and therefore cannot "
                "be approved for the jobseeker."
            )

        st.stop()


# ============================================================
# JOBSEEKER VIEW
# ============================================================

if demo_role == "Jobseeker":

    st.markdown(
        '<div class="diamond-kicker">DIAMOND · MOVEᴱ</div>',
        unsafe_allow_html=True
    )

    st.title("Your recommended learning")

    st.markdown(
        '<div class="diamond-subtitle">'
        'Learning opportunities approved for you based on your '
        'ᴱGROW profile, existing skills and learning needs.'
        '</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="prototype-note">'
        '<strong>Prototype demonstration:</strong> '
        'This version uses synthetic data.'
        '</div>',
        unsafe_allow_html=True
    )

    approved_ids = (
        st.session_state.approvals_by_user.get(
            profile.user_id,
            []
        )
    )

    if not approved_ids:

        st.info(
            "There are currently no caseworker-approved "
            "learning recommendations available for you."
        )

        st.caption(
            "In the full system, recommendations become "
            "visible after the caseworker review step."
        )

        st.stop()

    approved_recommendations = (
        jobseeker_output[
            jobseeker_output[
                "course_id"
            ].isin(
                approved_ids
            )
        ]
        .copy()
        .sort_values("rank")
        .reset_index(drop=True)
    )

    if approved_recommendations.empty:

        st.info(
            "There are currently no approved recommendations "
            "available in this recommendation run."
        )

        st.stop()

    # --------------------------------------------------------
    # COURSE DETAIL
    # --------------------------------------------------------

    if (
        st.session_state.viewed_course
        is not None
    ):

        if (
            st.session_state.viewed_course
            not in set(
                approved_recommendations[
                    "course_id"
                ]
            )
        ):

            st.session_state.viewed_course = None
            st.rerun()

        detail = (
            approved_recommendations[
                approved_recommendations[
                    "course_id"
                ]
                == st.session_state.viewed_course
            ]
            .iloc[0]
        )

        if st.button(
            "← Back to recommended learning"
        ):

            close_course()
            st.rerun()

        st.title(detail["title"])

        st.write(
            f"**Provider:** {detail['provider']}"
        )

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

        st.subheader(
            "Why this learning opportunity may fit you"
        )

        for reason in detail[
            "reasons_for_fit"
        ]:

            st.write(f"✓ {reason}")

        if len(
            detail[
                "micro_credentials"
            ]
        ) > 0:

            st.subheader(
                "Micro-credentials"
            )

            for credential in detail[
                "micro_credentials"
            ]:

                st.write(f"• {credential}")

        st.subheader(
            "Things to consider"
        )

        if detail["tradeoffs"]:

            for tradeoff in detail[
                "tradeoffs"
            ]:

                st.write(f"• {tradeoff}")

        else:

            st.write(
                "No major trade-offs identified."
            )

        st.divider()

        if (
            detail["course_id"]
            in st.session_state.signed_up_courses
        ):

            st.success(
                "✓ You have signed up for this course."
            )

        else:

            if st.button(
                "Sign up",
                key=(
                    f"user_signup_detail_"
                    f"{profile.user_id}_"
                    f"{detail['course_id']}"
                ),
                type="primary"
            ):

                sign_up_for_course(
                    detail["course_id"]
                )

                st.rerun()

        st.stop()

    # --------------------------------------------------------
    # APPROVED RECOMMENDATION CARDS
    # --------------------------------------------------------

    st.caption(
        f"Simulated participant: {profile.user_id}"
    )

    st.write("")

    for _, row in (
        approved_recommendations
        .iterrows()
    ):

        with st.container(
            border=True
        ):

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

            st.write(
                "**Why this may fit you**"
            )

            for reason in row[
                "reasons_for_fit"
            ]:

                st.write(f"✓ {reason}")

            button_col1, button_col2, _ = (
                st.columns(
                    [1, 1, 2]
                )
            )

            with button_col1:

                if st.button(
                    "View course",
                    key=(
                        f"user_view_"
                        f"{profile.user_id}_"
                        f"{row['course_id']}"
                    )
                ):

                    open_course(
                        row["course_id"]
                    )

                    st.rerun()

            with button_col2:

                if (
                    row["course_id"]
                    in st.session_state.signed_up_courses
                ):

                    st.success(
                        "✓ Signed up"
                    )

                else:

                    if st.button(
                        "Sign up",
                        key=(
                            f"user_signup_"
                            f"{profile.user_id}_"
                            f"{row['course_id']}"
                        ),
                        type="primary"
                    ):

                        sign_up_for_course(
                            row["course_id"]
                        )

                        st.rerun()

    if st.session_state.signed_up_courses:

        st.divider()

        st.subheader(
            "Courses you have signed up for"
        )

        signed_up_approved = (
            approved_recommendations[
                approved_recommendations[
                    "course_id"
                ].isin(
                    st.session_state.signed_up_courses
                )
            ]
        )

        for _, course in (
            signed_up_approved.iterrows()
        ):

            st.write(
                f"✓ **{course['title']}**"
            )

        st.info(
            "In the full DIAMOND workflow, course sign-ups "
            "would be recorded and communicated to the "
            "relevant learning platform."
        )

    st.divider()

    st.caption(
        "DIAMOND MOVEᴱ recommender prototype · "
        "powered by ᴱGROW profiling · "
        "synthetic data for demonstration purposes only."
    )
