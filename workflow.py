"""Lesson-specific workflow. Read this file before the execution adapter."""
from __future__ import annotations
import asyncio
import json
from pathlib import Path
from runtime import atomic_json, contained_path, in_process_tool

def churn(model, wait_hours):
    if wait_hours < 0:
        raise ValueError('Wait hours cannot be negative')
    return max(0.0, min(1.0, model['baseline_churn'] + model['wait_coefficient'] * wait_hours))


async def run(agent, data):
    baseline = churn(data, data['wait_hours'])
    intervention = churn(data, data['intervene_wait_hours'])
    assumptions = {'equation': 'churn = clamp(baseline + coefficient * wait_hours, 0, 1)', 'coefficient_source': 'supplied assumption, not estimated causal evidence'}
    explanation = await agent.ask('causal_interpretation', 'Explain the model intervention and its identification limitations. Do not call an assumed coefficient a demonstrated causal effect.',
        {'baseline': baseline, 'intervention': intervention, 'assumptions': assumptions}, 'Under the assumed model, reducing wait from 8 to 2 hours changes churn from 0.26 to 0.14. This is not an empirically established causal effect.')
    return {'model': assumptions, 'baseline_prediction': baseline, 'intervention_prediction': intervention, 'model_difference': intervention - baseline, 'explanation': explanation}
