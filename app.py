from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
import numpy as np
from datetime import datetime
from fairpyx import Instance, AllocationBuilder
from fairpyx.algorithms import hffd
import io
import logging
import re
print(hffd, 'hffd')  # This will use your GitHub implementation


app = Flask(__name__)
app.secret_key = 'your-secret-key-here'  # Change this in production

# Add context processor for current year
@app.context_processor
def inject_now():
    return {'now': datetime.now()}

def check_ido(agents):
    """
    Check if the input satisfies Identical-Order Preference (IDO).
    For each pair of items (i,j), if any agent considers i more costly than j,
    then all agents must consider i at least as costly as j.
    """
    num_items = len(agents[0])
    for i in range(num_items):
        for j in range(i + 1, num_items):
            # Check if any agent considers i more costly than j
            any_i_more_than_j = any(agent[i] > agent[j] for agent in agents)
            
            # If any agent considers i more costly than j, check that all agents
            # consider i at least as costly as j
            if any_i_more_than_j:
                if not all(agent[i] >= agent[j] for agent in agents):
                    return False, (i, j)
    
    return True, None

def validate_input(agents_data, thresholds_data):
    """
    Validate the input parameters for HFFD algorithm
    """
    try:
        # Parse agents' valuations
        agents = []
        for agent_data in agents_data:
            values = [float(x.strip()) for x in agent_data.split(',')]
            if not all(v >= 0 for v in values):
                return False, "All values must be non-negative"
            agents.append(values)
        
        # Check all agents have same number of items
        if not all(len(a) == len(agents[0]) for a in agents):
            return False, "All agents must have the same number of items"
        
        # Check IDO property
        is_ido, conflict = check_ido(agents)
        if not is_ido:
            i, j = conflict
            return False, f"Input violates IDO property: Agents disagree on relative ordering of items {i} and {j}"
        
        # Parse thresholds
        thresholds = [float(t.strip()) for t in thresholds_data.split(',')]
        if len(thresholds) != len(agents):
            return False, "Number of thresholds must match number of agents"
        if not all(t > 0 for t in thresholds):
            return False, "All thresholds must be positive"

        return True, (agents, thresholds)
    except ValueError:
        return False, "Please enter valid numbers"


def generate_random_input(num_agents: int | None = None,
                          num_chores:  int | None = None,
                          low_min:      int = 1,
                          high_min:     int = 6,
                          low_gap:      int = 1,
                          high_gap:     int = 10,
                          max_attempts: int = 30):
    """
    מחזיר קלט רנדומלי שמקיים IDO (Increasing Differences of Opinion).

    • num_agents / num_chores – אם None יוגרלו (2-5, 5-10).
    • low_min..high_min       – טווח ערך החפץ הקטן ביותר.
    • low_gap..high_gap       – טווח הפערים בין חפצים סמוכים (חיובי ⇒ שומר דירוג).
    • max_attempts            – מספר ניסיונות לייצר וקטורים ייחודיים ו-IDO.

    מחזיר dict:
        {
          'agents'    : ["v1,v2,..."],  # לכל סוכן
          'thresholds': "t1,t2,..."
        }
    """
    if num_agents is None:
        num_agents = np.random.randint(2, 6)   # 2-5
    if num_chores is None:
        num_chores = np.random.randint(5, 11)  # 5-10

    attempts = 0
    while attempts < max_attempts:
        attempts += 1
        valuations = []

        # ─── 1) בונים וקטור *נפרד* לכל סוכן ───
        for _ in range(num_agents):
            # ערך החפץ "הכי זול"
            min_val = np.random.randint(low_min, high_min)

            # פערים חיוביים אקראיים בין חפצים סמוכים
            gaps = np.random.randint(low_gap, high_gap, size=num_chores - 1)

            v = np.empty(num_chores, dtype=int)
            v[-1] = min_val
            # הולכים מהחפץ האחרון (הזול) לראשון (היקר)
            for i in range(num_chores - 2, -1, -1):
                v[i] = v[i + 1] + gaps[i]

            valuations.append(v)

        valuations = np.vstack(valuations)

        # ─── 2) ודא ייחודיות בין הסוכנים ───
        if len({tuple(row) for row in valuations}) < num_agents:
            continue

        # ─── 3) בדיקת IDO (כל הסוכנים שומרים אותו סדר) ───
        is_ido, _ = check_ido(valuations)      # מניח שקיימת פונקציה
        if not is_ido:
            continue

        # ─── 4) חישוב ספים ───
        thresholds = np.ceil(valuations.sum(axis=1) / num_agents).astype(int)

        return {
            'agents': [','.join(map(str, row)) for row in valuations],
            'thresholds': ','.join(map(str, thresholds))
        }

    # במקרים חריגים – קריאה רקורסיבית (נדיר שצריך)
    return generate_random_input(num_agents, num_chores,
                                 low_min, high_min, low_gap, high_gap, max_attempts)

@app.route('/')
def index():
    """Main entrance page"""
    return render_template('index.html')

@app.route('/form')
def form():
    """Form page for input parameters"""
    return render_template('form.html')

@app.route('/process', methods=['POST'])
def process():


    """Process the algorithm with input validation"""
    agents_data = request.form.getlist('agent_data[]')
    thresholds_data = request.form.get('thresholds', '').strip()

    if not agents_data or not thresholds_data:
        flash('Please provide all required data', 'error')
        return redirect(url_for('form'))

    # Validate input
    is_valid, result = validate_input(agents_data, thresholds_data)

    if not is_valid:
        flash(result, 'error')
        return redirect(url_for('form'))

    agents, thresholds = result
    
    # Create fairpyx instance
    instance = Instance(valuations=np.array(agents))
    builder = AllocationBuilder(instance)
    
    # Run algorithm
    try:
        result = hffd(builder, thresholds=thresholds)
        
        # Store results in session or pass as URL parameters
        return redirect(url_for('result',
                              agents_data=','.join(['|'.join(map(str, a)) for a in agents]),
                              thresholds_data=','.join(map(str, thresholds))))
    except Exception as e:
        flash(f'Error processing algorithm: {str(e)}', 'error')
        return redirect(url_for('form'))


@app.route('/result')
def result():
    # Setup a log capture stream
    log_stream = io.StringIO()
    stream_handler = logging.StreamHandler(log_stream)
    logger = logging.getLogger('fairpyx.algorithms.hffd')
    logger.setLevel(logging.INFO)
    logger.addHandler(stream_handler)
    agents_data = request.args.get('agents_data', '')
    thresholds_data = request.args.get('thresholds_data', '')

    if not agents_data or not thresholds_data:
        flash('No input data provided', 'error')
        return redirect(url_for('form'))

    # Parse stored data
    agents = [list(map(float, a.split('|'))) for a in agents_data.split(',')]
    thresholds = {i: float(t.strip()) for i, t in enumerate(thresholds_data.split(','))}

    # Create instance
    valuations = np.array(agents)
    instance = Instance(valuations=valuations)

    # # Run algorithm using fairpyx.divide (correct API)
    from fairpyx import divide
    allocations = divide(hffd, instance, thresholds=thresholds)

    # Calculate total costs
    total_costs = {}
    for agent, items in allocations.items():
        if items:
            total_costs[agent] = sum(agents[agent][item] for item in items)
        else:
            total_costs[agent] = 0
#########################
    stream_handler.flush()
    log_contents = log_stream.getvalue()

    # Clean up the handler so it doesn't duplicate logs next time
    logger.removeHandler(stream_handler)

    # Use regex to extract unallocated items from log
    match = re.search(r"Unallocated chores: \[(.*?)\]", log_contents)
    if match:
        unallocated = [int(x.strip()) for x in match.group(1).split(',')]
    else:
        unallocated = []
    ########################
    steps = []
    bundle_pattern = re.compile(r"Bundle #(\d+) → agent (\d+) : \[(.*?)\]")

    for line in log_contents.splitlines():
        match = bundle_pattern.search(line)
        if match:
            step_num = int(match.group(1))
            agent_id = int(match.group(2))
            bundle = [int(x.strip()) for x in match.group(3).split(',') if x.strip()]
            steps.append({
                'step': step_num,
                'agent': agent_id,
                'bundle': bundle,
                'description': f"Bundle {bundle} was assigned to agent {agent_id}."
            })

    return render_template('result.html',
                           agents=agents,
                           thresholds=thresholds,
                           allocations=allocations,
                           total_costs=total_costs,
                           steps=steps,
                           unallocated=unallocated,  # optional
                           timestamp=datetime.now().strftime('%Y-%m-%d %H:%M:%S'))


@app.route('/generate_random', methods=['POST'])
def generate_random():
    """Generate random input for demonstration"""
    num_agents = request.form.get('num_agents', type=int)
    num_chores = request.form.get('num_chores', type=int)
    random_input = generate_random_input(num_agents=num_agents, num_chores=num_chores)
    return jsonify(random_input)

if __name__ == '__main__':
    app.run(debug=True)
