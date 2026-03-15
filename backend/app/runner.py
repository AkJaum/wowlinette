import os
import inspect
import importlib
import re


def _has_exercise_dirs(path):
    """Return True when path contains at least one direct exNN directory."""
    try:
        for item in os.listdir(path):
            item_path = os.path.join(path, item)
            if os.path.isdir(item_path) and re.match(r"^ex\d{2}$", item):
                return True
    except OSError:
        return False
    return False


def _count_exercise_dirs(path):
    """Count direct exNN directories in path."""
    count = 0
    try:
        for item in os.listdir(path):
            item_path = os.path.join(path, item)
            if os.path.isdir(item_path) and re.match(r"^ex\d{2}$", item):
                count += 1
    except OSError:
        return 0
    return count


def _find_module_dir(base):
    """Find the directory that contains exercises regardless of zip/root folder name."""
    # Case 1: exercises are extracted directly in base (no root folder in zip).
    if _has_exercise_dirs(base):
        return base

    candidates = []
    for item in os.listdir(base):
        item_path = os.path.join(base, item)
        if os.path.isdir(item_path) and _has_exercise_dirs(item_path):
            candidates.append((item, item_path, _count_exercise_dirs(item_path)))

    if not candidates:
        return None

    # Keep current behavior preference when a cNN directory exists.
    c_module_candidates = [c for c in candidates if re.match(r"^c\d{2}$", c[0])]
    if c_module_candidates:
        c_module_candidates.sort(key=lambda x: x[0])
        return c_module_candidates[0][1]

    # Otherwise, pick the folder with more exercises; tie-break by folder name.
    candidates.sort(key=lambda x: (-x[2], x[0]))
    return candidates[0][1]

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

    # Find the exercise root directory from structure, not from zip/folder naming.
    module_dir = _find_module_dir(base)
    
    if not module_dir:
        return {
            "status": "error",
            "message": "No valid exercise structure found (expected ex00, ex01, etc.)",
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
