import { NextRequest } from 'next/server';

const BACKEND_URL = process.env.BACKEND_URL || 'http://localhost:8000';

type Params = {
  traceId: string;
};

export async function GET(
  request: NextRequest,
  { params }: { params: Params }
) {
  const { traceId } = params;

  // Create a TransformStream for SSE
  const encoder = new TextEncoder();
  const stream = new TransformStream();
  const writer = stream.writable.getWriter();

  // Helpful headers to reduce buffering by proxies/CDNs
  const proxyHeaders: HeadersInit = {
    'Accept': 'text/event-stream',
    'Cache-Control': 'no-cache, no-transform',
    'Connection': 'keep-alive',
  };

  // Connect to backend SSE endpoint
  const backendUrl = `${BACKEND_URL}/api/stream/${traceId}`;

  // Start the SSE connection to backend
  fetch(backendUrl, { headers: proxyHeaders })
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
          if (line.startsWith('data: ')) {
            // Forward the SSE data line as-is
            await writer.write(encoder.encode(line + '\n'));
            // Flush record separator
            await writer.write(encoder.encode('\n'));
          } else if (line.trim().length === 0) {
            // preserve boundaries
            await writer.write(encoder.encode('\n'));
          }
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
      'Content-Type': 'text/event-stream; charset=utf-8',
      'Cache-Control': 'no-cache, no-transform',
      'Connection': 'keep-alive',
      'X-Accel-Buffering': 'no',
      // Safari friendliness
      'Transfer-Encoding': 'chunked',
    },
  });
}
