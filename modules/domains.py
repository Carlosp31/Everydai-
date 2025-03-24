import modules.handling_fuctions.hd_culinary as hd_culinary
import modules.handling_fuctions.hd_gym as hd_gym
import modules.handling_fuctions.hd_fashion as hd_fashion
from typing_extensions import override
from openai import AssistantEventHandler
 
# First, we create a EventHandler class to define
# how we want to handle the events in the response stream.

class EventHandler(AssistantEventHandler):    
  @override
  def on_text_created(self, text) -> None:
    print(f"\nassistant > ", end="", flush=True)
      
  @override
  def on_text_delta(self, delta, snapshot):
    print(delta.value, end="", flush=True)
      
  def on_tool_call_created(self, tool_call):
    print(f"\nassistant > {tool_call.type}\n", flush=True)
  
  def on_tool_call_delta(self, delta, snapshot):
    if delta.type == 'code_interpreter':
      if delta.code_interpreter.input:
        print(delta.code_interpreter.input, end="", flush=True)
      if delta.code_interpreter.outputs:
        print(f"\n\noutput >", flush=True)
        for output in delta.code_interpreter.outputs:
          if output.type == "logs":
            print(f"\n{output.logs}", flush=True)




def chat_response(model, user_input, client, thread_idf, assistant_idf):
    response_2= None 
    message = client.beta.threads.messages.create(
    thread_id=thread_idf,
    role="user",
    content=user_input
    )

    run = client.beta.threads.runs.create_and_poll(
        thread_id=thread_idf,
        assistant_id= assistant_idf

    )
    print(f"Estado del assistant: {run.status}")
    if run.status == 'completed': 
        messages = client.beta.threads.messages.list(thread_id=thread_idf)
        # Filtrar los mensajes del asistente
        mensajes_asistente = [msg for msg in messages.data if msg.role == 'assistant']
        if mensajes_asistente:
            # Obtener el último mensaje del asistente
            ultimo_mensaje = mensajes_asistente[0]  # Accede al último mensaje del asistente
            for block in ultimo_mensaje.content:
                print(f"Assistant: {block.text.value}") 
                response= block.text.value# Imprime solo el contenido del último mensaje
                return response, response_2
        else:
            print("No se encontró un mensaje del asistente.")
    elif run.status == "requires_action":
       if model=="Cooking":
            response, response_2 = hd_culinary.hd_culinary(user_input, client, thread_idf, assistant_idf, run)
       elif model=="Fitness":
            response, response_2 = hd_gym.hd_gym(user_input, client, thread_idf, assistant_idf, run)
       elif model=="fashion":
            response, response_2 = hd_fashion.hd_fashion(user_input, client, thread_idf, assistant_idf, run)
       return response, response_2