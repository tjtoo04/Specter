def detect_friction(state):
     """
     Detect if the agent is experiencing friction (stuck/confused)

     Arguments:
        state: dictinary from StateTacker.update()

    returns:
        tuple: (is_stuck: bool, friction_type: str or None)

    Examples:
        (True, "Time_STUCK")  - Agent stuck too long
        (True, "Repeated_actions") - trying the same thing over and over
        (False, None)               - Everything normal  
    
     """

     #Rule 1 : Too long on same screen
     if state["time_on_screen"] > 15:
          return True, "Time_STUCK"
     
     #Rule 2: Too many attempts on same screen
     if state ["attempts_on_screen"] >=3:
          return True, "REPEATED_ACTIONS"
     
     #Rule 3: Seen this screen too many time (looping)
     if state ["screen_repeat_count"] >= 2:
          return True, "SCREEN_LOOP"
     
     #Rule 4: Action failed to execute
     if not state ["action_succeeded"]:
          return True, "Action_FAILED"
     
     #No friction detected
     return False, None