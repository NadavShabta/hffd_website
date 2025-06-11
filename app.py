from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
import numpy as np
from datetime import datetime
from hffd_algorithm import hffd, AllocationBuilder, Instance

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

def generate_random_input():
    """Generate random input for demonstration that satisfies IDO using positive integers"""
    num_agents = np.random.randint(2, 5)
    num_items = np.random.randint(5, 10)
    
    # Generate base valuations that satisfy IDO
    # First, generate a random number of unique values
    num_unique_values = np.random.randint(3, min(8, num_items + 1))
    unique_values = np.sort(np.random.randint(1, 10, size=num_unique_values))[::-1]  # Sort in descending order
    
    # Then, randomly assign these values to items, allowing some items to have equal values
    base_valuations = np.random.choice(unique_values, size=num_items)
    
    # Generate agent-specific multipliers (all positive integers)
    multipliers = np.random.randint(1, 3, size=num_agents)
    
    # Create valuations for each agent
    valuations = np.array([base_valuations * m for m in multipliers])
    
    # Verify IDO property
    is_ido, conflict = check_ido(valuations)
    if not is_ido:
        # If somehow we generated invalid input, try again
        return generate_random_input()
    
    # Generate thresholds that are reasonable given the valuations
    max_valuation = np.max(valuations)
    thresholds = np.random.randint(max_valuation * 2, max_valuation * 4, size=num_agents)
    
    return {
        'agents': [','.join(map(str, row)) for row in valuations],
        'thresholds': ','.join(map(str, thresholds))
    }

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
    """Result page with visualization"""
    agents_data = request.args.get('agents_data', '')
    thresholds_data = request.args.get('thresholds_data', '')

    if not agents_data or not thresholds_data:
        flash('No input data provided', 'error')
        return redirect(url_for('form'))

    # Parse stored data
    agents = [list(map(float, a.split('|'))) for a in agents_data.split(',')]
    thresholds = list(map(float, thresholds_data.split(',')))

    # Create instance and run algorithm
    instance = Instance(valuations=np.array(agents))
    builder = AllocationBuilder(instance)
    algorithm_result = hffd(builder, thresholds=thresholds)

    # Calculate total costs for each agent
    total_costs = {}
    for agent, items in algorithm_result['allocations'].items():
        if items:
            total_costs[agent] = sum(agents[agent][item] for item in items)
        else:
            total_costs[agent] = 0

    return render_template('result.html',
                         agents=agents,
                         thresholds=thresholds,
                         allocations=algorithm_result['allocations'],
                         total_costs=total_costs,
                         steps=algorithm_result['steps'],
                         unallocated=algorithm_result['unallocated'],
                         timestamp=datetime.now().strftime('%Y-%m-%d %H:%M:%S'))

@app.route('/generate_random', methods=['POST'])
def generate_random():
    """Generate random input for demonstration"""
    random_input = generate_random_input()
    return jsonify(random_input)

if __name__ == '__main__':
    app.run(debug=True)
