import { NextRequest } from 'next/server';

const BACKEND_URL = process.env.BACKEND_URL || 'http://localhost:8000';

export async function GET(
  request: NextRequest,
  { params }: { params: { traceId: string } }
) {
  const { traceId } = params;

  // Create a TransformStream for SSE
  const encoder = new TextEncoder();
  const stream = new TransformStream();
  const writer = stream.writable.getWriter();

  // Connect to backend SSE endpoint
  const backendUrl = `${BACKEND_URL}/api/stream/${traceId}`;

  // Start the SSE connection to backend
  fetch(backendUrl, {
    headers: {
      'Accept': 'text/event-stream',
      'Cache-Control': 'no-cache',
    },
  })
    .then(async (response) => {
      if (!response.ok) {
        await writer.write(encoder.encode(`data: ${JSON.stringify({ type: 'error', message: 'Failed to connect to backend' })}\n\n`));
        await writer.close();
        return;
      }

      const reader = response.body?.getReader();
      if (!reader) {
        await writer.write(encoder.encode(`data: ${JSON.stringify({ type: 'error', message: 'No response body' })}\n\n`));
        await writer.close();
        return;
      }

      const decoder = new TextDecoder();
      let buffer = '';

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        buffer += decoder.decode(value, { stream: true });
        const lines = buffer.split('\n');
        buffer = lines.pop() || '';

        for (const line of lines) {
          if (line.trim()) {
            // Forward the SSE data
            await writer.write(encoder.encode(line + '\n'));
          }
        }

        // Ensure double newline for SSE format
        if (lines.length > 0) {
          await writer.write(encoder.encode('\n'));
        }
      }

      await writer.close();
    })
    .catch(async (error) => {
      console.error('SSE streaming error:', error);
      await writer.write(encoder.encode(`data: ${JSON.stringify({ type: 'error', message: error.message })}\n\n`));
      await writer.close();
    });

  // Return SSE response
  return new Response(stream.readable, {
    headers: {
      'Content-Type': 'text/event-stream',
      'Cache-Control': 'no-cache',
      'Connection': 'keep-alive',
      'X-Accel-Buffering': 'no',
    },
  });
}
