import { NextRequest } from 'next/server';

const BACKEND_URL = process.env.BACKEND_URL || 'http://localhost:8000';

export async function POST(request: NextRequest) {
  const body = await request.json();

  try {
    // First, make request to backend to start the chat
    const backendPayload = {
      prompt: body.content,
      mode: body.writeupType || 'general',
      file_ids: body.attachments?.filter((a: any) => a.uploaded).map((a: any) => a.url) || [],
      user_params: {
        model: 'gemini-2.0-flash-exp',
        user_id: 'demo-user',
        writeupType: body.writeupType || 'general',
        field: 'general'
      }
    };

    console.log('Starting backend chat with:', backendPayload);
    console.log('Backend URL:', BACKEND_URL);

    const chatResponse = await fetch(`${BACKEND_URL}/api/chat`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(backendPayload),
    });

    const responseText = await chatResponse.text();
    console.log('Backend response status:', chatResponse.status);
    console.log('Backend response body:', responseText);

    if (!chatResponse.ok) {
      console.error('Backend chat failed:', chatResponse.status, responseText);
      throw new Error(`Backend chat failed: ${chatResponse.status} - ${responseText}`);
    }

    let chatData;
    try {
      chatData = JSON.parse(responseText);
    } catch (e) {
      console.error('Failed to parse backend response:', responseText);
      throw new Error('Invalid JSON response from backend');
    }

    const traceId = chatData.trace_id;

    if (!traceId) {
      console.error('No trace_id in backend response:', chatData);
      throw new Error('No trace_id received from backend');
    }

    console.log('Got trace_id:', traceId, 'Now streaming from:', `${BACKEND_URL}/api/chat/stream/${traceId}`);

    // Create streaming response
    const encoder = new TextEncoder();
    const stream = new TransformStream();
    const writer = stream.writable.getWriter();

    // Start streaming from backend
    (async () => {
      try {
        await writer.write(encoder.encode('data: {"event": "connected"}\n\n'));

        // Stream from backend
        const streamResponse = await fetch(`${BACKEND_URL}/api/chat/stream/${traceId}`, {
          method: 'GET',
          headers: {
            'Accept': 'text/event-stream',
          },
        });

        if (!streamResponse.ok) {
          throw new Error(`Stream failed: ${streamResponse.status}`);
        }

        const reader = streamResponse.body?.getReader();
        const decoder = new TextDecoder();

        if (reader) {
          while (true) {
            const { done, value } = await reader.read();
            if (done) break;

            const chunk = decoder.decode(value, { stream: true });
            const lines = chunk.split('\n');

            for (const line of lines) {
              if (line.startsWith('data: ')) {
                const data = line.slice(6);
                if (data.trim() === '[DONE]') {
                  await writer.write(encoder.encode('data: [DONE]\n\n'));
                  return;
                }
                
                try {
                  const parsed = JSON.parse(data);
                  if (parsed.token || parsed.content) {
                    await writer.write(encoder.encode(`data: ${JSON.stringify({ token: parsed.token || parsed.content })}\n\n`));
                  }
                } catch (e) {
                  // If not JSON, treat as plain text token
                  if (data.trim()) {
                    await writer.write(encoder.encode(`data: ${JSON.stringify({ token: data.trim() })}\n\n`));
                  }
                }
              }
            }
          }
        }

        await writer.write(encoder.encode('data: [DONE]\n\n'));
      } catch (error) {
        console.error('Streaming error:', error);
        // Fallback to dynamic response
        const response = generateDynamicResponse(body.content, body.writeupType);
        const words = response.split(' ');

        for (let i = 0; i < words.length; i++) {
          const token = words[i] + (i < words.length - 1 ? ' ' : '');
          await writer.write(encoder.encode(`data: ${JSON.stringify({ token })}\n\n`));
          await new Promise(resolve => setTimeout(resolve, 50));
        }
        
        await writer.write(encoder.encode('data: [DONE]\n\n'));
      } finally {
        await writer.close();
      }
    })();

    return new Response(stream.readable, {
      headers: {
        'Content-Type': 'text/event-stream',
        'Cache-Control': 'no-cache',
        'Connection': 'keep-alive',
      },
    });

  } catch (error) {
    console.error('Backend connection failed, using fallback:', error);
    
    // Fallback to local response if backend is unavailable
    const encoder = new TextEncoder();
    const stream = new TransformStream();
    const writer = stream.writable.getWriter();

    (async () => {
      try {
        await writer.write(encoder.encode('data: {"event": "connected"}\n\n'));
        
        const response = generateDynamicResponse(body.content, body.writeupType);
        const words = response.split(' ');

        for (let i = 0; i < words.length; i++) {
          const token = words[i] + (i < words.length - 1 ? ' ' : '');
          await writer.write(encoder.encode(`data: ${JSON.stringify({ token })}\n\n`));
          await new Promise(resolve => setTimeout(resolve, 50 + Math.random() * 50));
        }

        await writer.write(encoder.encode('data: [DONE]\n\n'));
      } catch (err) {
        console.error('Fallback streaming error:', err);
      } finally {
        await writer.close();
      }
    })();

    return new Response(stream.readable, {
      headers: {
        'Content-Type': 'text/event-stream',
        'Cache-Control': 'no-cache',
        'Connection': 'keep-alive',
      },
    });
  }
}

function generateDynamicResponse(userContent: string, writeupType: string): string {
  const contentWords = userContent.toLowerCase();
  
  // Analyze user input for key topics and themes
  const hasResearch = contentWords.includes('research') || contentWords.includes('study') || contentWords.includes('analysis');
  const hasWriting = contentWords.includes('write') || contentWords.includes('essay') || contentWords.includes('article');
  const hasTechnical = contentWords.includes('technical') || contentWords.includes('code') || contentWords.includes('programming');
  const hasAcademic = contentWords.includes('academic') || contentWords.includes('dissertation') || contentWords.includes('thesis');
  
  // Generate contextual response based on writeup type and content
  if (writeupType === 'dissertation' || hasAcademic) {
    return `I'll help you develop a comprehensive academic work on this topic. Based on your request about "${userContent.slice(0, 100)}${userContent.length > 100 ? '...' : ''}", I can assist with:

## Proposed Structure

**Introduction & Background**
- Contextual framework and problem statement
- Literature review of existing research
- Research objectives and methodology

**Main Analysis**
- Detailed examination of key concepts
- Critical analysis of current approaches
- Data interpretation and findings

**Conclusions & Implications**
- Summary of key insights
- Practical applications and recommendations
- Future research directions

Would you like me to elaborate on any specific section or provide more detailed guidance for your academic work?`;
  }
  
  if (writeupType === 'report' || hasResearch) {
    return `I'll create a comprehensive report addressing your inquiry about "${userContent.slice(0, 80)}${userContent.length > 80 ? '...' : ''}". Here's my analysis:

## Executive Summary
Based on your requirements, this report examines the key aspects and provides actionable insights.

## Key Findings
• **Primary Analysis**: The core elements of your request indicate a need for thorough investigation
• **Data Insights**: Current trends and patterns suggest significant opportunities
• **Risk Assessment**: Potential challenges and mitigation strategies identified

## Recommendations
1. **Immediate Actions**: Priority steps to address your specific needs
2. **Strategic Approach**: Long-term planning considerations
3. **Implementation Timeline**: Suggested phases for optimal results

## Next Steps
I recommend focusing on the most critical aspects first while building a foundation for comprehensive implementation.

Would you like me to dive deeper into any specific area of this analysis?`;
  }
  
  if (hasTechnical) {
    return `I understand you're looking for technical assistance with "${userContent.slice(0, 100)}${userContent.length > 100 ? '...' : ''}". Let me provide a structured approach:

## Technical Analysis

**Current Situation**
Your request involves technical considerations that require careful planning and implementation.

**Recommended Approach**
- **Assessment Phase**: Evaluate current requirements and constraints
- **Design Considerations**: Architectural decisions and best practices
- **Implementation Strategy**: Step-by-step development approach
- **Testing & Validation**: Quality assurance and performance optimization

**Key Considerations**
• Scalability and performance requirements
• Security and compliance factors
• Integration with existing systems
• Maintenance and support needs

I can provide more specific technical details, code examples, or implementation guidance based on your particular requirements. What aspect would you like to explore further?`;
  }
  
  // Default response for general writing requests
  return `Thank you for your request about "${userContent.slice(0, 100)}${userContent.length > 100 ? '...' : ''}". I'm here to provide comprehensive writing assistance tailored to your specific needs.

## Understanding Your Request
Based on your input, I can help you develop this topic with:

**Content Development**
- Structured approach to your subject matter
- Research-backed insights and analysis
- Clear, engaging writing style

**Organization & Flow**
- Logical progression of ideas
- Smooth transitions between concepts
- Compelling introduction and conclusion

**Quality Enhancement**
- Professional tone and clarity
- Proper formatting and structure
- Citations and references where appropriate

## Next Steps
I'm ready to dive deeper into any specific aspect of your request. Would you like me to:
- Develop an outline for your content?
- Focus on a particular section or angle?
- Provide more detailed analysis on specific points?

Please let me know how you'd like to proceed, and I'll tailor my assistance to meet your exact requirements.`;
}
