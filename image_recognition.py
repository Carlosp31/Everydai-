from openai import OpenAI


def img_openai(assistant, thread, image):
    client = OpenAI()
    file = client.files.create(
    file=open("image11.jpeg", "rb"),
    purpose="vision"
    )
    message= client.beta.threads.create(
    messages=[
        {
        "role": "user",
        "content": [
            {
            "type": "text",
            "text": "qué ves en la imagen"
            },
            {
            "type": "image_file",
            "image_file": {"file_id": file.id}
            },
        ],
        }
    ]
    )
    run = client.beta.threads.runs.create_and_poll(
    thread_id=thread.id,
    assistant_id=assistant.id,
    instructions="Actúa como un maestro culinario e identifica los ingredientes en la imagen. "
    )
    if run.status == 'completed': 
        messages = client.beta.threads.messages.list(thread_id=thread.id)

        # Filtrar los mensajes del asistente
        mensajes_asistente = [msg for msg in messages.data if msg.role == 'assistant']
        print(messages)
        if mensajes_asistente:
            # Obtener el último mensaje del asistente
            ultimo_mensaje = mensajes_asistente[0]  # Accede al último mensaje del asistente
            for block in ultimo_mensaje.content:
                print(f"Assistant: {block.text.value}")  # Imprime solo el contenido del último mensaje
        else:
            print("No se encontró un mensaje del asistente.")
    else:
        print(run.status)