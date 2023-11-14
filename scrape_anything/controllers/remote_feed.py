from ..browser import *
from ..view import *
from ..think import *
from ..act import *
from .controller import Controller
from .data_types import IncommingData,OutGoingData,EnabledActions,Error
from queue import Queue



class RemoteFeedController(Controller):

    def __init__(self,incoming_data_queue:Queue,outgoing_data_queue:Queue,status_queue:Queue,user_task:str,max_loops:int) -> None:
        super(RemoteFeedController,self).__init__(user_task)
        self.incoming_data_queue = incoming_data_queue
        self.outgoing_data_queue = outgoing_data_queue
        self.status_queue = status_queue
        self.is_closed = False
        self.max_loops = max_loops
        self.message_count = 0

    def fetch_infomration_on_screen(self,output_folder:str,loop_num:int):

        incoming_data:IncommingData = self.incoming_data_queue.get()
        # compute the elements on screen, current + change
        file_name_html = None

        return self.process_screen_data(incoming_data,output_folder,loop_num,file_name_html=file_name_html)

    
    def count_and_close(self):
        self.message_count=+1;
        return self.message_count == self.max_loops
    
    def take_action(self,tool_executor:ToolInterface,tool_input,num_loops:int,output_folder:str):

        self.outgoing_data_queue.put(OutGoingData(
                                                  session_closed=self.count_and_close(),
                                                  script=tool_executor.example_script,
                                                  tool_input=tool_executor.process_tool_arg(**tool_input)))
        
        execution_status = self.status_queue.get()
        if type(execution_status) is str:
            raise ValueError(f"execution failed: {execution_status}")

    def on_action_extraction_failed(self):
        self.outgoing_data_queue.put(Error(
            error_message="server_fault_retry",
            user_should_retry=True,
            session_closed=self.count_and_close(),
            )
        )
        
    def on_action_extraction_fatal(self):
        self.outgoing_data_queue.put(Error(
            error_message="server_fault_contact_admin",
            is_fatel=True,
            session_closed=self.count_and_close()
            )
        )

    def is_closed(self):
        self.is_closed

    def unpickle(self, output_folder, loop_num):
        data = super().unpickle(output_folder, loop_num)
        self.incoming_data_queue.put(data)
        
    def close(self):
        self.is_closed = True
        # if not self.is_closed:
        #     self.outgoing_data_queue.put(Error(error_message="server_limit_reach",is_fatel=True))