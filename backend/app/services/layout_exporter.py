from app.services.layout_engine import LayoutDocument, QuestionLayout


def export_layout(layout: LayoutDocument) -> dict:
    return {
        "sheetId": layout.sheet_id,
        "paperTitle": layout.paper_title,
        "pageSize": layout.page_size,
        "unit": layout.unit,
        "coordinateSystem": layout.coordinate_system,
        "pages": [
            {
                "pageIndex": layout.page.page_index,
                "width": layout.page.width,
                "height": layout.page.height,
                "positionMarks": [
                    {
                        "name": mark.name,
                        "x": mark.x,
                        "y": mark.y,
                        "width": mark.width,
                        "height": mark.height,
                    }
                    for mark in layout.page.position_marks
                ],
                "sections": [
                    {
                        "type": section.type,
                        "title": section.title,
                        "questions": [export_question(question) for question in section.questions],
                    }
                    for section in layout.page.sections
                ],
            }
        ],
    }


def export_question(question: QuestionLayout) -> dict:
    payload = {
        "questionNo": question.question_no,
        "type": question.type,
    }
    if question.options:
        payload["options"] = [
            {
                "option": option.option,
                "x": option.x,
                "y": option.y,
                "radius": option.radius,
            }
            for option in question.options
        ]
    else:
        payload["x"] = question.x
        payload["y"] = question.y
        payload["width"] = question.width
        payload["height"] = question.height
    return payload
