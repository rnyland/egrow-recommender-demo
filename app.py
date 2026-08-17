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
# LOAD RECOMMENDATION DATA
# ============================================================

@st.cache_data
def load_recommendations():
    return pd.read_pickle(
        "REC_USER_0001_20260817_073927_jobseeker_output.pkl"
    )


jobseeker_output = load_recommendations()


# ============================================================
# SESSION STATE
# ============================================================

if "interested_courses" not in st.session_state:
    st.session_state.interested_courses = []

if "viewed_course" not in st.session_state:
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
# CHECK DATA
# ============================================================

if jobseeker_output.empty:
    st.warning("No recommendations are currently available.")
    st.stop()


user_id = jobseeker_output.iloc[0]["user_id"]


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:

    st.title("EGROW")

    st.subheader("My profile")

    st.write(f"**User:** {user_id}")

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
