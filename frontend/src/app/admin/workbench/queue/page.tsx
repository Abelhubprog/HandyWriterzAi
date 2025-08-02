"use client";

import React, { useState, useEffect } from 'react';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import { createAssignment, claimNext, AssignmentSummary, CreateAssignmentRequest } from '@/services/workbench';
import { AssignmentCard } from '@/components/workbench/AssignmentCard';
import { ClaimButton } from '@/components/workbench/ClaimButton';
import { EmptyState } from '@/components/workbench/EmptyState';
import { nanoid } from 'nanoid';

// Placeholder for your actual auth context/hook
const useUser = () => {
  // In a real app, this would return user info including roles and tenant_id
  return {
    isAuthenticated: true,
    user: { id: 'user-admin-123', tenant_id: 'tenant-abc', role: 'admin', checker_id: 1 }, // Mock admin user
  };
};

export default function AdminWorkbenchQueuePage() {
  const { isAuthenticated, user } = useUser();
  const router = useRouter();
  const [claimedAssignment, setClaimedAssignment] = useState<AssignmentSummary | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!isAuthenticated || user?.role !== 'admin') {
      // Redirect to login or unauthorized page
      // router.push('/login');
      setError("Unauthorized access. Admin role required.");
    }
  }, [isAuthenticated, user, router]);

  const handleCreateAssignment = async () => {
    setLoading(true);
    setError(null);
    try {
      // Example: Create a dummy assignment for testing
      const dummyAssignment: CreateAssignmentRequest = {
        title: `Test Assignment - ${new Date().toLocaleString()}`,
        requirements: {
          min_similarity_score: 0.0,
          max_similarity_score: 5.0,
          expected_ai_score: 0.0,
        },
        delivery_channel: "workbench",
        source_conversation_id: `conv-${nanoid()}`, // Link to a dummy conversation
        ai_metadata: { "agent_decision": "manual_test" },
      };
      const newAssignment = await createAssignment(dummyAssignment);
      setClaimedAssignment(newAssignment); // Show the newly created one
      alert(`Assignment created: ${newAssignment.id}`);
    } catch (err: any) {
      setError(err.message || "Failed to create assignment.");
    } finally {
      setLoading(false);
    }
  };

  const handleClaimNext = async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await claimNext();
      if (response.id) {
        setClaimedAssignment({
          id: response.id,
          title: response.title || 'No Title',
          status: response.status || 'unknown',
          created_at: response.created_at || new Date().toISOString(),
          assigned_checker_id: response.assigned_checker_id,
        });
        alert(`Claimed assignment: ${response.id}`);
      } else {
        setClaimedAssignment(null);
        alert(response.message);
      }
    } catch (err: any) {
      setError(err.message || "Failed to claim next assignment.");
    } finally {
      setLoading(false);
    }
  };

  if (error) {
    return <div className="text-red-500 p-4">{error}</div>;
  }

  if (!isAuthenticated || user?.role !== 'admin') {
    return <div className="text-center p-8">Loading or Unauthorized...</div>;
  }

  return (
    <div className="container mx-auto p-4">
      <h1 className="text-3xl font-bold mb-6">Admin Workbench Queue</h1>

      <div className="mb-6 flex space-x-4">
        <button
          onClick={handleCreateAssignment}
          disabled={loading}
          className="bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded disabled:opacity-50"
        >
          {loading ? 'Creating...' : 'Create Dummy Assignment'}
        </button>
        <ClaimButton onClick={handleClaimNext} loading={loading} />
      </div>

      {claimedAssignment ? (
        <div className="bg-gray-800 p-6 rounded-lg shadow-lg">
          <h2 className="text-2xl font-semibold mb-4">Claimed Assignment</h2>
          <AssignmentCard summary={claimedAssignment} />
          <div className="mt-4">
            <Link href={`/checker/workbench/task?assignmentId=${claimedAssignment.id}`} className="text-blue-400 hover:underline mr-4">
              Go to Checker Task
            </Link>
            <Link href={`/admin/workbench/assignments/${claimedAssignment.id}`} className="text-green-400 hover:underline">
              View Assignment Details (Admin)
            </Link>
          </div>
        </div>
      ) : (
        <EmptyState message="No assignments claimed yet. Click 'Claim Next' or 'Create Dummy Assignment'." />
      )}

      {/* Optionally list other assignments in queue here */}
      {/* <h2 className="text-2xl font-semibold mt-8 mb-4">Assignments in Queue</h2>
      <p>List of other assignments would go here...</p> */}
    </div>
  );
}
