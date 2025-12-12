# services/bench_model.py

def calculate_bench_probability(skill, experience):
    """
    Simple rule-based bench probability.
    Returns float between 0 and 1 (rounded to 2 decimals).
    """
    skills=[]
    if skill is None:
        skills = []
    elif isinstance(skill, list):
        skills = [str(s).strip().lower() for s in skill if str(s).strip()]
    try:
        exp = float(experience)
    except Exception:
        exp = 0.0

    prob = 0.50


    if exp < 1:
        prob += 0.30
    elif exp < 2:
        prob += 0.15
    elif exp<=4:
        prob-=0.10
    elif exp >= 5:
        prob -= 0.20

    
    rare_skills = {"c#", "csharp", "sql", "react", "rust", "cybersecurity", "ai", "ml", "machine learning", "data engineering", "spark", "genai", "golang", "go", "kubernetes", "aws", "azure"}

    if not skills:
        skill_effect = 0.0
    else:
        effects = []
        for s in skills:
            normalized = s.replace('.', '').replace('#', 'sharp').strip()
            if any(rs in normalized for rs in rare_skills):
                # in-demand / rare skill reduces bench chance more
                effects.append(-0.12)
            else:
                # general additional skills still reduce bench chance slightly
                effects.append(-0.04)

        # Combine effects: take average and apply diminishing returns using sqrt(n)
        import math
        avg_effect = sum(effects) / len(effects)
        skill_effect = avg_effect * math.sqrt(len(effects))

 
    try:
        prob += skill_effect
    except Exception:
        pass

    
    prob = max(0.0, min(1.0, prob))
    return str(int(round(prob*100))) + "%"
