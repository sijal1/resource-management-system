from flask import Flask, request, jsonify
from flask_cors import CORS
from google import genai
from services.AIchat_response_provider import employee_response, refresh_data

from services.bench_model import calculate_bench_probability
from services.workday_calculator import calculate_working_days
from services.projects_client import get_all_projects

app = Flask(__name__)
CORS(app)
client = genai.Client(api_key="YOUR_GOOGLE_GENAI_API_KEY")


try:
    refresh_data()
    print("[INFO] Backend data loaded successfully")
except Exception as e:
    print(f"[WARNING] Failed to load backend data: {e}")

@app.route("/bench-probability", methods=["POST"])
def bench_probability():
    data = request.get_json(force=True)

    skill = data.get("skill")
    experience = float(data.get("experience", 0))

    prob = calculate_bench_probability(skill, experience)

    return jsonify({
        "success": True,
        "bench_probability": prob
    })


# 2) Working Days for Each Project

@app.route("/working-days", methods=["GET"])
def working_days():
    projects = get_all_projects()

    results = []

    for p in projects:
        # Extract proper date part: YYYY-MM-DD
        start = p.get("startDate", "")[:10]
        end = p.get("endDate", "")[:10]

        if not start or not end:
            continue

        wd = calculate_working_days(start, end)

        results.append({
            "projectID": p.get("projectID"),
            "projectName": p.get("projectName"),
            "workingDays": wd
        })

    return jsonify({
        "success": True,
        "working_days": results
    })


@app.route("/chatbot", methods=["POST"])
def chatbot():

    user_message = request.json.get("message", "")

    try:
        '''call function to fetch the responses for backend'''
        API_DATA_JSON=employee_response
        print(employee_response)
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

    
    system_instruction = """
    You are an intelligent HR & Employee & Project Resource chatbot.
    You MUST answer strictly using ONLY the data provided in the "JSON Data" section.
    If the answer is not present in that data, reply:
    "I don't have information about that."

    Never guess. Never hallucinate.
    """

   
    prompt = f"""
    SYSTEM INSTRUCTION:
    {system_instruction}

    USER QUESTION:
    {user_message}

    EMPLOYEE DATA (JSON):
    {API_DATA_JSON}
    """

    answer = None
    
    try:
        ai_response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
            config={
                "temperature": 0.15,
                "top_p": 0.9,
                "top_k": 80,
                "max_output_tokens": 500
            }
        )

        try:
            answer = ai_response.candidates[0].content.parts[0].text
        except:
            pass
        
        if not answer:
            try:
                for p in ai_response.candidates[0].content.parts:
                    if hasattr(p, "text") and p.text:
                        answer = p.text
                        break
            except:
                pass

        if not answer:
            answer = "The model returned no text due to a safety filter or empty response."
    
    except Exception as e:
        print(f"[ERROR] Gemini API call failed: {e}")
        import traceback
        traceback.print_exc()
        answer = f"Error calling AI model: {str(e)}"

    
    return jsonify({"response": answer})


if __name__ == "__main__":
    app.run(port=5001, debug=False)
