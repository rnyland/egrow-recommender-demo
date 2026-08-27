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

# Clear cached data while testing updated synthetic datasets
st.cache_data.clear()


@st.cache_data(show_spinner=False)
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
# ORGANISATIONS
# ============================================================

# Purpose: Defines the six DIAMOND organisations used in the prototype.

ORGANISATIONS = [
    "EMIT",
    "YPDE",
    "DEINDE",
    "FOB",
    "PROM",
    "FMIR"
]


# Check that the new simulated datasets contain the required organisation fields.
if "organisation" not in jobseekers.columns:
    st.error(
        "The jobseeker dataset is missing the 'organisation' column."
    )
    st.stop()

if "provider" not in courses.columns:
    st.error(
        "The course dataset is missing the 'provider' column."
    )
    st.stop()


# Keep only recognised DIAMOND organisations.
jobseekers = jobseekers[
    jobseekers["organisation"].isin(ORGANISATIONS)
].copy()

courses = courses[
    courses["provider"].isin(ORGANISATIONS)
].copy()

# ============================================================
# DEMO ROLE + SELECT JOBSEEKER
# ============================================================

# Purpose: Selects the system role and restricts access by organisation.

demo_role = st.sidebar.radio(
    "Demo as",
    options=[
        "Caseworker",
        "Jobseeker"
    ],
    index=0
)


# ------------------------------------------------------------
# CASEWORKER
# ------------------------------------------------------------

if demo_role == "Caseworker":

    # Simulates which DIAMOND organisation the caseworker belongs to.
    caseworker_organisation = st.sidebar.selectbox(
        "Caseworker organisation",
        options=ORGANISATIONS
    )

    # Caseworkers can only access applicants from their own organisation.
    eligible_jobseekers = jobseekers[
        jobseekers["organisation"]
        == caseworker_organisation
    ].copy()

    user_selector_label = (
        "Select applicant to review"
    )


# ------------------------------------------------------------
# APPLICANT
# ------------------------------------------------------------

else:

    caseworker_organisation = None

    # Simulated login: all applicants can be selected for testing.
    eligible_jobseekers = jobseekers.copy()

    user_selector_label = (
        "Simulated applicant login"
    )


user_options = (
    eligible_jobseekers["user_id"]
    .sort_values()
    .tolist()
)


if not user_options:

    st.sidebar.warning(
        "No simulated applicants are available "
        "for this organisation."
    )

    st.stop()


selected_user_id = st.sidebar.selectbox(
    user_selector_label,
    options=user_options
)


# Retrieves the selected applicant's complete record.
selected_user = (
    jobseekers[
        jobseekers["user_id"]
        == selected_user_id
    ]
    .iloc[0]
)


# Organisation is stored directly in the applicant dataset.
applicant_organisation = (
    selected_user["organisation"]
)


# Safety check: a caseworker cannot access an applicant
# belonging to another organisation.
if (
    demo_role == "Caseworker"
    and applicant_organisation
    != caseworker_organisation
):

    st.error(
        "Access denied: caseworkers can only review "
        "applicants from their own organisation."
    )

    st.stop()


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

# Approves a course only when caseworker, applicant and provider match.
def approve_course(
    user_id,
    course_id,
    caseworker_organisation
):

    applicant_row = (
        jobseekers[
            jobseekers["user_id"]
            == user_id
        ]
        .iloc[0]
    )

    course_row = (
        courses[
            courses["course_id"]
            == course_id
        ]
        .iloc[0]
    )

    applicant_org = (
        applicant_row["organisation"]
    )

    course_provider = (
        course_row["provider"]
    )

    if (
        applicant_org
        != caseworker_organisation
        or course_provider
        != applicant_org
    ):

        return False

    approved = (
        st.session_state.approvals_by_user
        .setdefault(
            user_id,
            []
        )
    )

    if course_id not in approved:
        approved.append(course_id)

    return True

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
learning_styles = selected_user["learning_styles"] 

# ============================================================
# PROFILE EXTRACTION
# ============================================================

# Purpose: Builds and checks a structured profile for the selected applicant.

from dataclasses import dataclass, field
from typing import Optional


@dataclass
class JobSeekerProfile:

    user_id: str
    organisation: str

    digital_class: int
    digital_profile: str
    digital_level: str

    green_class: int
    green_profile: str

    age: Optional[int]
    country: Optional[str]
    city: Optional[str]

    education_level: Optional[str]
    employment_status: Optional[str]

    learning_styles: Optional[str]
    accessibility_need: Optional[str]

    missing_fields: list = field(
        default_factory=list
    )

    profile_confidence: str = "low"

    can_recommend: bool = False

    recommendation_blockers: list = field(
        default_factory=list
    )


# Defines the minimum information required for recommendations.
CRITICAL_PROFILE_FIELDS = [
    "organisation",
    "digital_profile",
    "green_profile",
    "learning_styles"
]


def extract_jobseeker_profile(user):

    # --------------------------------------------------------
    # Check required information
    # --------------------------------------------------------

    missing_fields = []

    for field_name in CRITICAL_PROFILE_FIELDS:

        value = user.get(
            field_name,
            None
        )

        if (
            value is None
            or pd.isna(value)
            or value == ""
        ):

            missing_fields.append(
                field_name
            )


    # --------------------------------------------------------
    # Profile confidence
    # --------------------------------------------------------

    if len(missing_fields) == 0:

        profile_confidence = "high"

    elif len(missing_fields) == 1:

        profile_confidence = "medium"

    else:

        profile_confidence = "low"


    # --------------------------------------------------------
    # Recommendation blockers
    # --------------------------------------------------------

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


    can_recommend = (
        len(blockers) == 0
    )


    # --------------------------------------------------------
    # Create structured applicant profile
    # --------------------------------------------------------

    profile = JobSeekerProfile(

        user_id=user["user_id"],

        organisation=user[
            "organisation"
        ],

        digital_class=int(
            user[
                "latent_class_digital"
            ]
        ),

        digital_profile=user[
            "digital_profile"
        ],

        digital_level=user[
            "digital_level"
        ],

        green_class=int(
            user[
                "latent_class_green"
            ]
        ),

        green_profile=user[
            "green_profile"
        ],

        age=(
            int(user["age"])
            if pd.notna(user["age"])
            else None
        ),

        country=user[
            "country"
        ],

        city=user[
            "city"
        ],

        education_level=user[
            "education_level"
        ],

        employment_status=user[
            "employment_status"
        ],


        learning_styles=user[
            "learning_styles"
        ],

        accessibility_need=user[
            "accessibility_need"
        ],

        missing_fields=missing_fields,

        profile_confidence=(
            profile_confidence
        ),

        can_recommend=can_recommend,

        recommendation_blockers=(
            blockers
        )
    )

    return profile


# Creates the profile for the currently selected applicant.
profile = extract_jobseeker_profile(
    selected_user
)


# ============================================================
# COURSE RETRIEVAL
# ============================================================

# Purpose: Retrieves all courses provided by the applicant's organisation.

def retrieve_candidate_courses(
    courses,
    applicant_organisation
):

    candidate_courses = (
        courses[
            courses["provider"]
            == applicant_organisation
        ]
        .copy()
        .reset_index(drop=True)
    )

    return candidate_courses


# An applicant can only be recommended courses from their organisation.
candidate_courses = retrieve_candidate_courses(
    courses=courses,
    applicant_organisation=profile.organisation
)


# ============================================================
# FEASIBILITY FILTER
# ============================================================

# Purpose: Removes courses that are not practically suitable for the applicant.

# Checks whether each course is feasible for the selected applicant.

def check_feasibility(profile, course):

    reasons = []

    # --------------------------------------------------------
    # Organisation / provider
    # --------------------------------------------------------

    # The applicant can only receive courses provided
    # by their own organisation.
    if (
        str(course["provider"]).upper()
        != str(profile.organisation).upper()
    ):

        reasons.append(
            "Course is provided by another organisation."
        )

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
        profile.learning_styles
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

# Converts digital levels into numbers so they can be compared.
# This also has to be done for green levels when these have been finalized.

DIGITAL_LEVEL_ORDER = {
    "low": 1,
    "medium": 2,
    "high": 3
}

# Digital fit and green fit contribute equally to the final score.

RANKING_WEIGHTS = {
    "digital_fit": 0.50,
    "green_fit": 0.50
}

# ------------------------------------------------------------
# A) DIGITAL FIT
# ------------------------------------------------------------

# Calculates how well the course's digital level matches the applicant.

def calculate_digital_fit(profile, course):

    user_level = DIGITAL_LEVEL_ORDER.get(
        str(profile.digital_level).lower(),
        0
    )

    course_level = DIGITAL_LEVEL_ORDER.get(
        str(
            course["digital_level_required"]
        ).lower(),
        0
    )

    # Calculates the distance between the applicant's level and the course level.

    # Fallback mechanism if an unexpected value occurs
    if user_level is None or course_level is None:
        return 0.0
    
    difference = abs(
        user_level - course_level
    )

    # Exact match
    if difference == 0:
        return 100.0

    # Applicant and course are one level apart
    elif difference == 1:
        return 75.0

    # Applicant and course are two levels apart
    elif difference == 2:
        return 50.0

    return 50.0

# ------------------------------------------------------------
# B) GREEN FIT
# ------------------------------------------------------------

# Calculates how closely the applicant's green capability
# matches the green level of the course.

def calculate_green_fit(
    profile,
    course
):

    # Converts green levels into a 1–3 scale.
    GREEN_LEVEL_ORDER = {
        "low": 1,
        "medium": 2,
        "high": 3
    }

    # Applicant's green level
    user_level = GREEN_LEVEL_ORDER.get(
        str(profile.green_profile).lower()
    )

    # Course's green level
    course_level = GREEN_LEVEL_ORDER.get(
        str(course["green_relevance"]).lower()
    )

    # Missing or unknown information
    if user_level is None or course_level is None:
        return 0.0

    # Calculate distance between applicant and course
    difference = abs(
        user_level - course_level
    )

    # Exact match
    if difference == 0:
        return 100.0

    # One level apart
    elif difference == 1:
        return 75.0

    # Two levels apart
    elif difference == 2:
        return 50.0

# ------------------------------------------------------------
# FINAL MATCH SCORE
# ------------------------------------------------------------

# Calculates the digital and green score for every feasible course
# and combines them into one final match score.

def rank_courses(
    profile,
    feasible_courses
):

    ranked_records = []

    # Assess every feasible course.
    for _, course in feasible_courses.iterrows():

        # Calculate digital fit
        digital_score = (
            calculate_digital_fit(
                profile,
                course
            )
        )

        # Calculate green fit
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

        # Add the scores to the course information
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

    # Convert results to dataframe
    ranked = pd.DataFrame(
        ranked_records
    )

    if ranked.empty:
        return ranked

    # Rank/Sorts courses from highest to lowest match score.
    
    ranked = (
        ranked
        .sort_values(
            "final_match_score",
            ascending=False
        )
        .reset_index(drop=True)
    )

    # Recommendation rank: Adds a ranking number to each course.
    
    ranked["rank"] = range(
        1,
        len(ranked) + 1
    )

    return ranked

# ------------------------------------------------------------
# RUN RANKING
# ------------------------------------------------------------

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

    if score >= 90:
        return "Very strong match"

    elif score >= 75:
        return "Strong match"

    elif score >= 50:
        return "Good match"

    else:
        return "Possible match"


def create_recommendation_explanation(
    profile,
    course
):

    reasons = []
    tradeoffs = []

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

        st.divider()

        st.subheader("Selected applicant")

        st.write(f"**Applicant:** {profile.user_id}")
        st.write(f"**Organisation:** {profile.organisation}")
        st.write(f"**Digital profile:** {profile.digital_profile}")
        st.write(f"**Green profile:** {profile.green_profile}")
        st.write(f"**Learning preference:** {profile.learning_styles}")

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

    st.title("Review recommended learning")

    st.write(
        "The system has already extracted the jobseeker profile, "
        "retrieved courses from the applicant organisation, applied the deterministic "
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

    # --------------------------------------------------------
    # JOBSEEKER PROFILE
    # --------------------------------------------------------

    st.subheader("Jobseeker profile")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.write(f"**User:** {profile.user_id}")
        st.write(f"**Organisation:** {profile.organisation}")
        st.write(f"**Employment:** {profile.employment_status}")

    with col2:
        st.write(f"**Digital:** {profile.digital_profile}")
        st.write(f"**Green:** {profile.green_profile}")

    with col3:
        st.write(f"**Delivery:** {profile.learning_styles}")
        st.write(f"**Confidence:** {profile.profile_confidence}")

    with st.expander("View additional profile information"):
        st.write(f"**Age:** {profile.age}")
        st.write(f"**Education:** {profile.education_level}")
        st.write(f"**Location:** {profile.city}, {profile.country}")
        st.write(f"**Accessibility need:** {profile.accessibility_need}")

    st.divider()

    # --------------------------------------------------------
    # CHECK WHETHER RECOMMENDATIONS CAN BE MADE
    # --------------------------------------------------------

    if not profile.can_recommend:

        st.error(
            "The profile is not complete enough for recommendations."
        )

        for blocker in profile.recommendation_blockers:
            st.write(f"• {blocker}")

        st.stop()

    # --------------------------------------------------------
    # NO RECOMMENDATIONS
    # --------------------------------------------------------

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
            "Only courses that pass the feasibility filter "
            "can enter the recommendation and approval process."
        )

        st.stop()

    # --------------------------------------------------------
    # APPROVAL CONTROLS
    # --------------------------------------------------------

    action_col1, action_col2, _ = st.columns(
        [1, 1, 2]
    )

    with action_col1:

        if st.button(
            "Approve all",
            type="primary"
        ):

            if (
                profile.organisation
                == caseworker_organisation
            ):

                same_org_course_ids = (
                    jobseeker_output[
                        jobseeker_output["provider"]
                        == profile.organisation
                    ]["course_id"]
                    .tolist()
                )

                st.session_state.approvals_by_user[
                    profile.user_id
                ] = same_org_course_ids

                st.rerun()

            else:

                st.error(
                    "Approval blocked: caseworker and "
                    "applicant organisations do not match."
                )

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

    # --------------------------------------------------------
    # RECOMMENDED COURSES
    # --------------------------------------------------------

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

            # ------------------------------------------------
            # INDIVIDUAL APPROVAL
            # ------------------------------------------------

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

                    approval_success = approve_course(
                        profile.user_id,
                        course_id,
                        caseworker_organisation
                    )

                    if approval_success:

                        st.rerun()

                    else:

                        st.error(
                            "Approval blocked: the caseworker, "
                            "applicant and course provider must "
                            "belong to the same organisation."
                        )

    # --------------------------------------------------------
    # CASEWORKER DECISION SUMMARY
    # --------------------------------------------------------

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




# ============================================================
# JOBSEEKER VIEW
# ============================================================

if demo_role == "Jobseeker":

    st.markdown(
        '<div class="diamond-kicker">DIAMOND · MOVEᴱ</div>',
        unsafe_allow_html=True
    )

    st.title("Your recommended learning")

    st.caption(
        f"Organisation: {profile.organisation}"
    )

    st.markdown(
        '<div class="diamond-subtitle">'
        'Learning opportunities approved for you.'
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
            &
            (
                jobseeker_output["provider"]
                == profile.organisation
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
