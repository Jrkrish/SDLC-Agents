from pydantic import BaseModel, Field
from typing import Optional, Union

class SDLCRequest(BaseModel):
    project_name: str = Field(..., 
                              example="Ecommerce Platform",
                              description="The name of the project")
    
    requirements: Optional[Union[str, list[str]]] = Field(None, 
                                                example="Users can browse products, add them to cart, make payments, and view order history",
                                                description="The requirements for the project (string or list)")
    task_id: Optional[str] = Field(None, 
                                    example="sdlc-session-5551defc",
                                    description="The task id of the workflow session")
    
    next_node: Optional[str] = Field(None, 
                                example="review_user_stories",
                                description="The node to be executed in the workflow. Pass the node information returned from previous API")
    
    status: Optional[str] = Field(None, 
                                example="approved or feedback",
                                description="The status of the review")
    
    feedback: Optional[str] = Field(None, 
                                example="The user stories are good but need to be more specific",
                                description="The feedback for the review")
