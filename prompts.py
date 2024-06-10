# text MMI classification prompts
text_mmi_prompts = {
    "Task": "You are a seismic expert. The epicenter of this earthquake is located at {epicenter}. Please assess the following text posted on Twitter for earthquake-related damage based on the Modified Mercalli Intensity (MMI) Scale: {text}. \n",
    "Output_format": "Return the result in this JSON format: {'MMI': 'your judgment', 'location': 'your identification', 'reason': 'your reasoning'}.",
    "Instruction": "1. If the text does not describe any {epicenter} earthquake-caused damage, return 'None' for MMI.\n"
                   "2. If the damage location is not mentioned in the text, return 'None' for location.\n"
                   "3. Provide your reasoning based on the details mentioned in the text.\n"
}

# image MMI classification prompts
image_mmi_prompts = {
    "Task": "You are a seismic expert. Please assess the following image posted on Twitter for earthquake-related damage based on the Modified Mercalli Intensity (MMI) Scale.\n",
    "Output_format": "Return the result in this JSON format: {'MMI': 'your judgement', 'reason': 'your reasoning'}.\n",
    "Instruction": "1. If the image does not describe any earthquake-caused damage, return 'None' for MMI.\n"
                   "2. Provide your reasoning based on the details described in the image.\n"
}


"""
Perhaps there are a lot of factors that should be considered. 
1. First-hand observations (e.g., residents report, local report, official report, etc.)
2. The location of the user (in-context location, registration location)
3. Whether the tweet is a noise to this task.
"""