import os
import inspect
import importlib
import re

def get_available_lists():
    """Discover all available test lists"""
    testes_dir = os.path.join(os.path.dirname(__file__), "testes")
    available_lists = []
    
    if os.path.exists(testes_dir):
        for filename in sorted(os.listdir(testes_dir)):
            if filename.startswith("list_") and filename.endswith(".py"):
                list_name = filename.replace(".py", "")
                available_lists.append(list_name)
    
    return available_lists

def run_all_tests(base, list_name="list_00"):
    """Run all tests from the specified list"""

    # Find the c00/c01/c02... directory within the extracted files
    module_dir = None
    for item in os.listdir(base):
        item_path = os.path.join(base, item)
        if os.path.isdir(item_path) and re.match(r"^c\d{2}$", item):
            module_dir = item_path
            break
    
    if not module_dir:
        return {
            "status": "error",
            "message": "No valid course module found (ex00, ex01, etc.)",
            "exercises": []
        }

    try:
        # Dynamically import the test module
        test_module = importlib.import_module(f"app.testes.{list_name}")
    except ImportError as e:
        return {
            "status": "error",
            "message": f"List '{list_name}' not found: {str(e)}",
            "exercises": []
        }

    # Get the passing exercise (nota de corte)
    passing_exercise = getattr(test_module, "PASSING_EXERCISE", None)
    
    if not passing_exercise:
        return {
            "status": "error",
            "message": f"PASSING_EXERCISE not defined in {list_name}",
            "exercises": []
        }

    # Discover all test functions from the imported module
    exercises = []
    for name, func in inspect.getmembers(test_module, inspect.isfunction):
        if name.startswith("test_"):
            exercise_name = name.replace("test_", "")
            exercises.append((exercise_name, func))

    # Sort by exercise name (ex00, ex01, ex02, ...)
    exercises.sort(key=lambda x: x[0])

    results = []
    passed_until_required = True

    for name, test in exercises:
        try:
            success = test(module_dir)
        except Exception as e:
            print(f"Error in {list_name}/{name}: {str(e)}")
            success = False

        results.append({
            "exercise": name,
            "success": success
        })
        
        # Check if this is the passing exercise and if it failed
        if name == passing_exercise and not success:
            passed_until_required = False

    # Determine overall status
    # Student passes if all exercises up to PASSING_EXERCISE are successful
    passed_status = True
    for result in results:
        if result["exercise"] <= passing_exercise:
            if not result["success"]:
                passed_status = False
                break
        else:
            # Don't require exercises after the passing exercise
            break

    return {
        "status": "approved" if passed_status else "failed",
        "passing_exercise": passing_exercise,
        "message": f"{'✅ Aprovado!' if passed_status else '❌ Reprovado'} (Nota de corte: {passing_exercise})",
        "exercises": results
    }
