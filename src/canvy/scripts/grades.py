# INFO: Postpone but not delete code because idk why I can't access these marks
import logging

from canvasapi.assignment import Assignment
from canvasapi.canvas import Canvas

logger = logging.getLogger(__name__)


def grades_by_course(_canvas: Canvas) -> dict[str, float | None]:
    ...
    # return {
    #     course.course_code: calculate_grading(assignment)
    #     for course in canvas.get_courses()
    #     for assignment in course.get_assignments()
    # }


def grades(_canvas: Canvas) -> dict[str, dict[str, float | None]]:
    ...
    # return {
    #     course.course_code: {
    #         assignment.name: calculate_grading(assignment)
    #         for assignment in course.get_assignments()
    #     }
    #     for course in canvas.get_courses()
    # }


def calculate_grading(_assignment: Assignment) -> float | None:
    ...
    # def grade_change_value(event: GradeChangeEvent) -> float:
    #     t = datetime.fromisoformat(event.created_at)
    #     return t.timestamp()

    # logger.info("Getting grade change events")
    # try:
    #     grade_events = list(assignment.get_grade_change_events())
    # except Exception as e:
    #     logger.warning(f"Error fetching grade events: {e}")
    #     return None
    # if not grade_events:
    #     logger.warning(f"Grade events for {assignment.name} are empty!")
    #     return None
    # grade_events.sort(key=grade_change_value)
    # last_event = grade_events.pop()
    # return last_event.grade_after / assignment.points_possible
