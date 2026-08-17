
import streamlit as st
import pandas as pd
import textwrap


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
# CUSTOM CSS
# ============================================================

st.markdown(
    """
    <style>

    .block-container {
        max-width: 1100px;
        padding-top: 1.5rem;
        padding-bottom: 3rem;
    }

    .egrow-header {
        border-bottom: 1px solid #e1e1e1;
        padding-bottom: 18px;
        margin-bottom: 30px;
    }

    .egrow-title {
        font-size: 28px;
        font-weight: 700;
        margin-bottom: 3px;
    }

    .egrow-breadcrumb {
        color: #6c757d;
        font-size: 14px;
    }

    .intro-box {
        padding: 5px 0 18px 0;
        margin-bottom: 10px;
    }

    .course-card {
        border: 1px solid #dedede;
        border-radius: 10px;
        padding: 24px;
        margin-bottom: 24px;
        background: white;
        box-shadow: 0px 2px 7px rgba(0,0,0,0.05);
    }

    .rank-text {
        color: #777;
        font-size: 13px;
        margin-bottom: 4px;
    }

    .course-title {
        font-size: 23px;
        font-weight: 650;
        margin-bottom: 4px;
    }

    .provider {
        color: #666;
        font-size: 14px;
        margin-bottom: 14px;
    }

    .match-badge {
        display: inline-block;
        padding: 6px 11px;
        border-radius: 18px;
        background: #e9f6ec;
        font-size: 13px;
        font-weight: 650;
        margin-bottom: 14px;
    }

    .course-meta {
        font-size: 14px;
        color: #444;
        margin-bottom: 18px;
    }

    .section-title {
        font-weight: 650;
        margin-top: 15px;
        margin-bottom: 7px;
    }

    .skill-badge {
        display: inline-block;
        background: #f1f3f5;
        border-radius: 15px;
        padding: 5px 10px;
        margin: 3px 4px 3px 0;
        font-size: 12px;
    }

    .success-box {
        padding: 12px 15px;
        background: #edf7ed;
        border-radius: 6px;
        margin-top: 10px;
        margin-bottom: 15px;
    }

    </style>
    """,
    unsafe_allow_html=True
)


# ============================================================
# HEADER
# ============================================================

st.markdown(
    textwrap.dedent("""
    <div class="egrow-header">
        <div class="egrow-title">
            EGROW Learning Platform
        </div>
        <div class="egrow-breadcrumb">
            My dashboard › Course recommendations
        </div>
    </div>
    """),
    unsafe_allow_html=True
)


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

    st.header("My profile")

    st.write(f"**User:** {user_id}")

    st.divider()

    st.write("### Navigation")

    st.write("🏠 Dashboard")
    st.write("📚 My courses")
    st.write("⭐ Recommended courses")
    st.write("👤 Profile")

    st.divider()

    if st.session_state.interested_courses:

        st.write("### Courses I'm interested in")

        interested_rows = jobseeker_output[
            jobseeker_output["course_id"].isin(
                st.session_state.interested_courses
            )
        ]

        for _, course in interested_rows.iterrows():
            st.write(f"• {course['title']}")

    else:
        st.caption(
            "Courses you mark as interesting will appear here."
        )


# ============================================================
# COURSE DETAIL VIEW
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

    if detail["micro_credentials"]:

        st.subheader("Micro-credentials")

        for credential in detail["micro_credentials"]:
            st.write(f"• {credential}")

    st.subheader("Things to consider")

    if detail["tradeoffs"]:
        for tradeoff in detail["tradeoffs"]:
            st.write(f"• {tradeoff}")
    else:
        st.write("No major trade-offs identified.")

    st.divider()

    if detail["course_id"] in st.session_state.interested_courses:

        st.success(
            "You have marked this course as interesting."
        )

    else:

        if st.button(
            "I'm interested",
            key=f"detail_interest_{detail['course_id']}",
            type="primary"
        ):
            mark_interested(detail["course_id"])
            st.rerun()

    st.stop()


# ============================================================
# MAIN RECOMMENDATION PAGE
# ============================================================

st.markdown(
    textwrap.dedent(f"""
    <div class="intro-box">
        <h2>Recommended courses for you</h2>

        <p>
            These recommendations are based on your current
            profile, career goals, skills and training preferences.
        </p>

        <span style="color:#777;font-size:13px;">
            Demo user: {user_id}
        </span>
    </div>
    """),
    unsafe_allow_html=True
)


# ============================================================
# COURSE CARDS
# ============================================================

for _, row in (
    jobseeker_output
    .sort_values("rank")
    .iterrows()
):

    skills_html = "".join(
        [
            f'<span class="skill-badge">{skill}</span>'
            for skill in row["skills_taught"]
        ]
    )

    reasons_html = "".join(
        [
            f"<li>{reason}</li>"
            for reason in row["reasons_for_fit"]
        ]
    )

    if row["tradeoffs"]:
        tradeoff_text = row["tradeoffs"][0]
    else:
        tradeoff_text = "No major trade-offs identified."

    st.markdown(
    textwrap.dedent(f"""
        <div class="course-card">

            <div class="rank-text">
                Recommendation #{int(row['rank'])}
            </div>

            <div class="course-title">
                {row['title']}
            </div>

            <div class="provider">
                {row['provider']}
            </div>

            <div class="match-badge">
                {row['match_label']}
                ·
                {row['final_match_score']}/100
            </div>

            <div class="course-meta">

                <strong>Delivery:</strong>
                {row['delivery_mode']}

                &nbsp;&nbsp;

                <strong>Language:</strong>
                {row['language']}

                &nbsp;&nbsp;

                <strong>Duration:</strong>
                {row['duration_weeks']} weeks

            </div>

            <div class="section-title">
                Why this course may fit you
            </div>

            <ul>
                {reasons_html}
            </ul>

            <div class="section-title">
                Skills you may develop
            </div>

            <div>
                {skills_html}
            </div>

            <div class="section-title">
                Things to consider
            </div>

            <div>
                {tradeoff_text}
            </div>

        </div>
    """),
    unsafe_allow_html=True
)

    col1, col2, col3 = st.columns(
        [1, 1, 3]
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
# DEMO FEEDBACK SUMMARY
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
# DEMO NOTICE
# ============================================================

st.divider()

st.caption(
    "EGROW recommender system prototype. "
    "This demonstration uses synthetic data only."
)
