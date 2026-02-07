import time

class StateTracker:
    def __init__(self):
        #Runs once when we create the tracker
        #It's like opening a fresh notebook

        self.current_screen_id = None 
        self.screen_enter_time = None      #when did I arrive here?
        self.screen_history = []           #where have i been ?( a list)
        self.attempts_on_screen = 0
        #self.last_actions = None

    def update(self,vision_output, action_result):

        '''
       Update state after an action

       Arguments:
                vision_output: dict with "screen_type" from vision.py
                action_result: dict with "success" from actions.py

        Returns: 
            dict: Current state metrics
        '''
        # to extract the current screen from screenshot
        screen_type = vision_output.get("screen_type","unknown")

        #to check if the screen changed
        if screen_type != self.current_screen_id:
            # Its a new screen, so we reset all the counters
            self.current_screen_id = screen_type
            self.screen_enter_time = time.time()
            self.attempts_on_screen = 0
            self.screen_history.append(screen_type)
        else:
            # Same screen, increments how many times on the same screen
            self.attempts_on_screen += 1

        # Calcultate time on current screen
        if self.screen_enter_time:
            time_on_screen = time.time() - self.screen_enter_time
        else:
            time_on_screen = 0
        
        #Count how many times we have already seen this screen
        screen_repeat_count = self.screen_history.count(self.current_screen_id)

        #Build state snapshot
        return {
            "Current_screen_id": self.current_screen_id,
            "time_on_Screen": round(time_on_screen, 1),
            "Screen_repeat_count": screen_repeat_count,
            "Attempts_on_screen":self.attempts_on_screen,
            "last_action":self.last_actions,
            "history":self.screen_history[-5:], # only last 5 screens
            "action_succeeded": action_result.get("success", False)
        }
    
    def set_last_action(self, action):
        """Remember what action we just tried."""
        self.last_action = action.get("action")