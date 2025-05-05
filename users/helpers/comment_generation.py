# +++++++++++++++++++++++++++++++++++++++++++++
# 📄 Intelligent Feedback Generator
# Description: Produces subject-wise exam feedback based on peer comparison
# +++++++++++++++++++++++++++++++++++++++++++++

def generate_intelligent_comment(subject, exam_title, grade, score, class_scores_same_grade):
    """
    Generates an intelligent feedback comment for a given exam result.

    Args:
        subject (str): Name of the subject.
        exam_title (str): Title of the exam.
        grade (str): Grade letter achieved (A-F).
        score (float): Student's score.
        class_scores_same_grade (List[float]): Scores of all students with the same grade in that exam.

    Returns:
        str: Smart feedback message.
    """

    # 🧪 Guard clause: Handle missing or invalid input
    if not grade or score is None:
        return "No grade or score available to generate feedback."

    # 🧮 Calculate average score among students with the same grade
    avg_grade_score = sum(class_scores_same_grade) / len(class_scores_same_grade) if class_scores_same_grade else 0
    delta = score - avg_grade_score  # Difference between student score and peer average

    # 🗒️ Start building comment with basic performance summary
    comment = f"You scored {round(score, 1)} in {subject}, which falls under grade {grade}. "

    # 🔠 Normalize to main grade band (e.g., A-, A+ → A)
    band = grade[0]

    # +++++++++++++++++++++++++++++
    # 🏆 Grade Band: A
    # +++++++++++++++++++++++++++++
    if band == "A":
        comment += f"This is the highest grade band. The average in this group is {avg_grade_score:.1f}. "
        if delta > 2:
            comment += "You're outperforming your peers — excellent work! 🏆"
        elif delta < -2:
            comment += "You're slightly below average for an A — you can dominate with a little push! 🔥"
        else:
            comment += "You're right around the average — still a top performer! ✨"

    # +++++++++++++++++++++++++++++
    # 📘 Grade Band: B
    # +++++++++++++++++++++++++++++
    elif band == "B":
        comment += f"The average among B-grade students is {avg_grade_score:.1f}. "
        if delta > 2:
            comment += "You're above your group — aim for an A next time! 🚀"
        elif delta < -2:
            comment += "You're slightly below your peers — keep pushing, an A is within reach!"
        else:
            comment += "You're on par with your group — solid performance. 📘"

    # +++++++++++++++++++++++++++++
    # ⚖️ Grade Band: C
    # +++++++++++++++++++++++++++++
    elif band == "C":
        comment += f"Your group's average is {avg_grade_score:.1f}. "
        if delta > 2:
            comment += "You're near the top of your group — aim for a B! ✊"
        elif delta < -2:
            comment += "You're lagging in this group — focus on key improvement areas. 🧠"
        else:
            comment += "You're right in the middle — stay consistent and improve!"

    # +++++++++++++++++++++++++++++
    # ⚠️ Grade Band: D
    # +++++++++++++++++++++++++++++
    elif band == "D":
        comment += f"This grade band averages {avg_grade_score:.1f}. "
        if delta > 2:
            comment += "You're slightly above average here — keep striving to exit this band."
        else:
            comment += "You're at risk — consider extra support and focused study. 💡"

    # +++++++++++++++++++++++++++++
    # 🚨 Grade Band: E
    # +++++++++++++++++++++++++++++
    elif band == "E":
        comment += "This is a very low grade band. Immediate support and revision is needed. 🙏"

    # +++++++++++++++++++++++++++++
    # ❌ Grade Band: F
    # +++++++++++++++++++++++++++++
    elif band == "F":
        comment += "You received a failing grade. Seek teacher guidance and commit to a study plan. 📚"

    # +++++++++++++++++++++++++++++
    # 🤷 Fallback for unknown grades
    # +++++++++++++++++++++++++++++
    else:
        comment += "Grade not recognized — please consult your teacher."

    return comment


def generate_subject_comments(student, marks):
    """
    Generates subject-specific comments based on performance in the student’s exams.

    Args:
        student (User): The student object.
        marks (QuerySet): List of StudentMark objects containing exam and grade details.

    Returns:
        List[dict]: A list of dictionaries with subject-wise exam feedback.
    """
    comments = []
    for mark in marks:
        if not mark.grade:
            continue

        # Get peer scores in same grade
        peer_scores = mark.exam.studentmark_set.filter(grade=mark.grade).values_list("score", flat=True)
        comment = generate_intelligent_comment(
            subject=mark.exam.subject.name,
            exam_title=mark.exam.title,
            grade=mark.grade,
            score=mark.score,
            class_scores_same_grade=list(peer_scores)
        )

        comments.append({
            "subject": mark.exam.subject.name,
            "exam_title": mark.exam.title,
            "grade": mark.grade,
            "comment": comment
        })

    return comments
