import { Message, OpenAIModel } from "@/types";
import { createParser, ParsedEvent, ReconnectInterval } from "eventsource-parser";


export const AIStream = async (messages: Message[]) => {
 const API_URL = process.env.API_URL;
 if (!API_URL) {
	throw new Error("Missing API_URL environment variable");
 }

  const encoder = new TextEncoder();
  const decoder = new TextDecoder();

    const res = await fetch(`${API_URL}/v1/chat/completions`, {
    headers: {
      "Content-Type": "application/json",
    },
    method: "POST",
    body: JSON.stringify({
      model:"gemma-3-1b-it-Q2_K.gguf",
      messages: [
        {
          role: "system",
          content: `You are a helpful, friendly, assistant and a employee of zendalona(A FOSS creates software for visually impared users).`
        },
        ...messages
      ],
      max_tokens: 800,
      temperature: 0.0,
      stream: true
    })
  });

  if (res.status !== 200) {
    throw new Error("returned an error");
  }

  const stream = new ReadableStream({
    async start(controller) {
      const onParse = (event: ParsedEvent | ReconnectInterval) => {
        if (event.type === "event") {
          const data = event.data;

          if (data === "[DONE]") {
            controller.close();
            return;
          }

          try {
            const json = JSON.parse(data);
            const text = json.choices[0].delta.content;
            const queue = encoder.encode(text);
            controller.enqueue(queue);
          } catch (e) {
            controller.error(e);
          }
        }
      };

      const parser = createParser(onParse);

      for await (const chunk of res.body as any) {
        parser.feed(decoder.decode(chunk));
      }
    }
  });

  return stream;
};
