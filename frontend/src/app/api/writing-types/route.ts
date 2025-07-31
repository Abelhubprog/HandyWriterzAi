import { NextResponse } from 'next/server';

export async function GET() {
  // Mock writing types - in production, this would come from a database
  const writingTypes = [
    { value: 'general', label: 'General' },
    { value: 'essay', label: 'Essay' },
    { value: 'report', label: 'Report' },
    { value: 'dissertation', label: 'PhD Dissertation' },
    { value: 'case_study', label: 'Case Study' },
    { value: 'market_research', label: 'Market Research' },
    { value: 'technical_report', label: 'Technical Report' },
    { value: 'presentation', label: 'Presentation' },
    { value: 'coding', label: 'Coding' },
  ];

  return NextResponse.json(writingTypes);
}
