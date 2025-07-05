#!/usr/bin/env python3
"""
REST API server for Project Orchestrator
Provides HTTP endpoints for the orchestrator functionality
"""

import os
import json
import logging
from flask import Flask, request, jsonify
from project_orchestrator import ProjectOrchestrator
from typing import Dict, Any

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)

# Initialize the orchestrator
orchestrator = ProjectOrchestrator()

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'service': 'SaaS Factory Project Orchestrator',
        'version': '0.1.0'
    })

@app.route('/orchestrator', methods=['POST'])
def orchestrator_endpoint():
    """Main orchestrator endpoint"""
    try:
        # Get request data
        if request.is_json:
            data = request.get_json()
        else:
            data = request.form.to_dict()
        
        logger.info(f"Received request: {data}")
        
        # Process the request
        result = orchestrator.process_request(data)
        
        logger.info(f"Orchestrator response: {result}")
        
        # Return the result
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Error processing request: {str(e)}")
        return jsonify({
            'status': 'error',
            'error': str(e)
        }), 500

@app.route('/orchestrator/simple', methods=['POST'])
def simple_orchestrator_endpoint():
    """Simple orchestrator endpoint for backward compatibility"""
    try:
        # Get request data
        if request.is_json:
            data = request.get_json()
        else:
            data = request.form.to_dict()
        
        logger.info(f"Received simple request: {data}")
        
        # Process the request using the simple run method
        result = orchestrator.run(data)
        
        logger.info(f"Simple orchestrator response: {result}")
        
        # Return the result
        return jsonify({
            'status': 'success',
            'result': result
        })
        
    except Exception as e:
        logger.error(f"Error processing simple request: {str(e)}")
        return jsonify({
            'status': 'error',
            'error': str(e)
        }), 500

@app.route('/orchestrator/agents', methods=['GET'])
def list_agents():
    """List available agents"""
    try:
        agents = list(orchestrator.agents.keys())
        return jsonify({
            'status': 'success',
            'agents': agents
        })
    except Exception as e:
        logger.error(f"Error listing agents: {str(e)}")
        return jsonify({
            'status': 'error',
            'error': str(e)
        }), 500

@app.route('/', methods=['GET'])
def root():
    """Root endpoint with basic info"""
    return jsonify({
        'service': 'SaaS Factory Project Orchestrator',
        'version': '0.1.0',
        'endpoints': {
            'health': '/health',
            'orchestrator': '/orchestrator',
            'simple': '/orchestrator/simple',
            'agents': '/orchestrator/agents'
        }
    })

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    debug = os.environ.get('FLASK_ENV') == 'development'
    
    logger.info(f"Starting SaaS Factory Project Orchestrator API on port {port}")
    app.run(host='0.0.0.0', port=port, debug=debug) 