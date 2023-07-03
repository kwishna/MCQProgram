import pandas as pd
from fastapi import FastAPI, Request, Form
from fastapi.exceptions import RequestValidationError
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.responses import JSONResponse
from starlette.status import HTTP_422_UNPROCESSABLE_ENTITY

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

questions_df = pd.read_excel("questions.xlsx")
positive_points = 10
negative_points = -5
current_question = 0
score = 0


@app.get("/", response_class=HTMLResponse)
async def read_item(request: Request):
    global current_question, score
    current_question = 0
    score = 0
    return templates.TemplateResponse("quiz.html", {"request": request, "current_question": current_question,
                                                    "question": questions_df.iloc[current_question],
                                                    "total_questions": len(questions_df)})


@app.post("/next")
async def next_question(request: Request, answer: str = Form(...)):
    global current_question, score
    if answer.lower() == questions_df.iloc[current_question]["Answer"].lower():
        score += positive_points
    else:
        score += negative_points
    current_question += 1
    if current_question >= len(questions_df):
        return templates.TemplateResponse("result.html", {"request": request, "score": score,
                                                          "total": len(questions_df) * positive_points})
    else:
        return templates.TemplateResponse("quiz.html", {"request": request, "current_question": current_question,
                                                        "question": questions_df.iloc[current_question],
                                                        "total_questions": len(questions_df)})


@app.post("/previous")
async def previous_question(request: Request, answer: str = Form(...)):
    global current_question, score
    if answer.lower() == questions_df.iloc[current_question]["Answer"].lower():
        score += positive_points
    else:
        score += negative_points
    current_question -= 1
    if current_question < 0:
        current_question = 0
    return templates.TemplateResponse("quiz.html", {"request": request, "current_question": current_question,
                                                    "question": questions_df.iloc[current_question],
                                                    "total_questions": len(questions_df)})

# @app.post("/submit")
# async def submit_quiz(request: Request, answer: str):
#     global score
#     if answer.lower() == questions_df.iloc[current_question]["Answer"].lower():
#         score += positive_points
#     else:
#         score += negative_points
#     total_marks = len(questions_df) * positive_points
#     return templates.TemplateResponse("result.html", {"request": request, "score": score, "total": total_marks})


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    for error in exc.errors():
        if error["type"] == "value_error.missing":
            return JSONResponse(
                status_code=HTTP_422_UNPROCESSABLE_ENTITY,
                content="YOU MUST SELECT AN OPTION TO MOVE FORWARD."
            )
    return JSONResponse(
        status_code=HTTP_422_UNPROCESSABLE_ENTITY,
        content="YOU MUST SELECT AN OPTION TO MOVE FORWARD."
    )
