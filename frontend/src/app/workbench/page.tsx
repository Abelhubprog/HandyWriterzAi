"use client";

import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Input } from '@/components/ui/input';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from '@/components/ui/dialog';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { 
  Download, 
  Upload, 
  Eye, 
  Clock, 
  FileText, 
  CheckCircle, 
  XCircle, 
  AlertCircle, 
  Search,
  Filter,
  Star,
  TrendingUp,
  Users,
  Calendar,
  LogOut,
  Shield,
  Settings,
  Loader2
} from 'lucide-react';
import { toast } from '@/components/ui/use-toast';
import { useWorkbenchAuth, withWorkbenchAuth } from '@/contexts/WorkbenchAuthContext';
import { useRouter } from 'next/navigation';
import { workbenchAPI, WorkbenchDocument } from '@/services/workbench-api';

export default withWorkbenchAuth(function WorkbenchPage() {
  const { user, logout, hasPermission, isAdmin } = useWorkbenchAuth();
  const router = useRouter();
  const [documents, setDocuments] = useState<WorkbenchDocument[]>([]);
  const [isLoadingDocuments, setIsLoadingDocuments] = useState(true);
  const [stats, setStats] = useState({
    totalDocuments: 0,
    availableDocuments: 0,
    inProgressDocuments: 0,
    completedDocuments: 0,
    flaggedDocuments: 0,
  });
  const [searchTerm, setSearchTerm] = useState('');
  const [categoryFilter, setCategoryFilter] = useState<string>('all');
  const [statusFilter, setStatusFilter] = useState<string>('all');
  const [sortBy, setSortBy] = useState<string>('uploadedAt');
  const [sortOrder, setSortOrder] = useState<'asc' | 'desc'>('desc');
  const [selectedDocument, setSelectedDocument] = useState<WorkbenchDocument | null>(null);
  const [showUploadDialog, setShowUploadDialog] = useState(false);
  const [uploadFiles, setUploadFiles] = useState<{
    plagiarismReport: File | null;
    aiReport: File | null;
  }>({ plagiarismReport: null, aiReport: null });

  // Load documents and stats on component mount
  useEffect(() => {
    loadDocuments();
    loadStats();
  }, []);

  // Reload documents when filters change
  useEffect(() => {
    loadDocuments();
  }, [searchTerm, categoryFilter, statusFilter]);

  const loadDocuments = async () => {
    try {
      setIsLoadingDocuments(true);
      const params: any = {};
      
      if (searchTerm) params.search = searchTerm;
      if (categoryFilter !== 'all') params.category = categoryFilter;
      if (statusFilter !== 'all') params.status = statusFilter;
      
      const fetchedDocuments = await workbenchAPI.getDocuments(params);
      setDocuments(fetchedDocuments);
    } catch (error) {
      console.error('Failed to load documents:', error);
      toast({
        title: "Error Loading Documents",
        description: "Failed to load documents. Please try again.",
        variant: "destructive"
      });
    } finally {
      setIsLoadingDocuments(false);
    }
  };

  const loadStats = async () => {
    try {
      const fetchedStats = await workbenchAPI.getWorkbenchStats();
      setStats({
        totalDocuments: fetchedStats.totalDocuments,
        availableDocuments: fetchedStats.availableDocuments,
        inProgressDocuments: fetchedStats.inProgressDocuments,
        completedDocuments: fetchedStats.completedDocuments,
        flaggedDocuments: fetchedStats.flaggedDocuments
      });
    } catch (error) {
      console.error('Failed to load stats:', error);
    }
  };

  // Filter and sort documents
  const filteredDocuments = documents
    .filter(doc => {
      const matchesSearch = doc.title.toLowerCase().includes(searchTerm.toLowerCase());
      const matchesCategory = categoryFilter === 'all' || doc.category === categoryFilter;
      const matchesStatus = statusFilter === 'all' || doc.status === statusFilter;
      return matchesSearch && matchesCategory && matchesStatus;
    })
    .sort((a, b) => {
      let aValue: any = a[sortBy as keyof WorkbenchDocument];
      let bValue: any = b[sortBy as keyof WorkbenchDocument];
      
      if (sortBy === 'uploadedAt' || sortBy === 'claimedAt') {
        aValue = new Date(aValue || 0).getTime();
        bValue = new Date(bValue || 0).getTime();
      }
      
      if (sortOrder === 'asc') {
        return aValue > bValue ? 1 : -1;
      } else {
        return aValue < bValue ? 1 : -1;
      }
    });

  const handleLogout = () => {
    logout();
    router.push('/workbench/login');
  };

  const handleClaimDocument = async (docId: string) => {
    if (!hasPermission('workbench.document.claim')) {
      toast({
        title: "Permission Denied",
        description: "You don't have permission to claim documents.",
        variant: "destructive"
      });
      return;
    }

    try {
      await workbenchAPI.claimDocument(docId);
      await loadDocuments(); // Refresh the list
      await loadStats(); // Update stats
      
      toast({
        title: "Document Claimed",
        description: "You have successfully claimed this document for checking.",
      });
    } catch (error: any) {
      toast({
        title: "Failed to Claim Document",
        description: error.message || "Please try again.",
        variant: "destructive"
      });
    }
  };

  const handleDownloadDocument = async (docId: string) => {
    if (!hasPermission('workbench.document.download')) {
      toast({
        title: "Permission Denied",
        description: "You don't have permission to download documents.",
        variant: "destructive"
      });
      return;
    }

    try {
      const blob = await workbenchAPI.downloadDocument(docId);
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.style.display = 'none';
      a.href = url;
      a.download = `document-${docId}.docx`;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);
      
      toast({
        title: "Download Started",
        description: "The document has been downloaded successfully.",
      });
    } catch (error: any) {
      toast({
        title: "Download Failed",
        description: error.message || "Please try again.",
        variant: "destructive"
      });
    }
  };

  const handleUploadReports = async (docId: string) => {
    if (!hasPermission('workbench.document.upload_reports')) {
      toast({
        title: "Permission Denied",
        description: "You don't have permission to upload reports.",
        variant: "destructive"
      });
      return;
    }

    if (!uploadFiles.plagiarismReport || !uploadFiles.aiReport) {
      toast({
        title: "Missing Files",
        description: "Please upload both plagiarism and AI detection reports.",
        variant: "destructive"
      });
      return;
    }

    try {
      await workbenchAPI.uploadReports(docId, {
        plagiarismReport: uploadFiles.plagiarismReport,
        aiReport: uploadFiles.aiReport
      });

      await loadDocuments(); // Refresh the list
      await loadStats(); // Update stats
      
      setShowUploadDialog(false);
      setUploadFiles({ plagiarismReport: null, aiReport: null });
      
      toast({
        title: "Reports Uploaded",
        description: "Your reports have been processed successfully.",
      });
    } catch (error: any) {
      toast({
        title: "Upload Failed",
        description: error.message || "Please try again.",
        variant: "destructive"
      });
    }
  };

  const handleMarkZero = async (docId: string) => {
    if (!hasPermission('workbench.document.upload_reports')) {
      toast({
        title: "Permission Denied",
        description: "You don't have permission to mark documents.",
        variant: "destructive"
      });
      return;
    }

    try {
      await workbenchAPI.markDocumentZero(docId);
      await loadDocuments(); // Refresh the list
      await loadStats(); // Update stats
      
      toast({
        title: "ZORO Marked",
        description: "Document marked as final. No further loops will be processed.",
      });
    } catch (error: any) {
      toast({
        title: "Failed to Mark Document",
        description: error.message || "Please try again.",
        variant: "destructive"
      });
    }
  };

  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case 'urgent': return 'bg-red-500';
      case 'high': return 'bg-orange-500';
      case 'normal': return 'bg-blue-500';
      case 'low': return 'bg-gray-500';
      default: return 'bg-gray-500';
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'available': return 'text-green-600';
      case 'claimed': return 'text-blue-600';
      case 'checking': return 'text-yellow-600';
      case 'completed': return 'text-green-600';
      case 'flagged': return 'text-red-600';
      default: return 'text-gray-600';
    }
  };

  const formatTimeAgo = (dateString: string) => {
    const now = new Date();
    const date = new Date(dateString);
    const diffInMinutes = Math.floor((now.getTime() - date.getTime()) / (1000 * 60));
    
    if (diffInMinutes < 60) return `${diffInMinutes}m ago`;
    if (diffInMinutes < 1440) return `${Math.floor(diffInMinutes / 60)}h ago`;
    return `${Math.floor(diffInMinutes / 1440)}d ago`;
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 to-gray-100 dark:from-gray-900 dark:to-gray-800">
      <div className="container mx-auto p-6">
        {/* Header */}
        <div className="flex justify-between items-center mb-8">
          <div>
            <h1 className="text-4xl font-bold text-gray-900 dark:text-white">
              Document Workbench
            </h1>
            <p className="text-gray-600 dark:text-gray-400 mt-2">
              Human-in-the-loop quality assurance platform
            </p>
          </div>
          <div className="flex items-center space-x-4">
            <Badge variant="outline" className="px-3 py-1">
              <Users className="w-4 h-4 mr-1" />
              {user?.username}
            </Badge>
            <Badge variant={user?.role === 'admin' ? 'default' : 'secondary'} className="px-3 py-1">
              {user?.role === 'admin' ? (
                <Shield className="w-4 h-4 mr-1" />
              ) : (
                <Star className="w-4 h-4 mr-1" />
              )}
              {user?.role}
            </Badge>
            <Button
              variant="outline"
              size="sm"
              onClick={handleLogout}
              className="flex items-center"
            >
              <LogOut className="w-4 h-4 mr-1" />
              Logout
            </Button>
          </div>
        </div>

        {/* Statistics Cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          <Card>
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-gray-600 dark:text-gray-400">Available</p>
                  <p className="text-2xl font-bold text-green-600">
                    {stats.availableDocuments}
                  </p>
                </div>
                <FileText className="w-8 h-8 text-green-600" />
              </div>
            </CardContent>
          </Card>
          
          <Card>
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-gray-600 dark:text-gray-400">In Progress</p>
                  <p className="text-2xl font-bold text-blue-600">
                    {stats.inProgressDocuments}
                  </p>
                </div>
                <Clock className="w-8 h-8 text-blue-600" />
              </div>
            </CardContent>
          </Card>
          
          <Card>
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-gray-600 dark:text-gray-400">Completed</p>
                  <p className="text-2xl font-bold text-green-600">
                    {stats.completedDocuments}
                  </p>
                </div>
                <CheckCircle className="w-8 h-8 text-green-600" />
              </div>
            </CardContent>
          </Card>
          
          <Card>
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-gray-600 dark:text-gray-400">Flagged</p>
                  <p className="text-2xl font-bold text-red-600">
                    {stats.flaggedDocuments}
                  </p>
                </div>
                <AlertCircle className="w-8 h-8 text-red-600" />
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Filters and Search */}
        <Card className="mb-6">
          <CardContent className="p-6">
            <div className="flex flex-wrap gap-4 items-center">
              <div className="flex-1 min-w-64">
                <div className="relative">
                  <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-4 h-4" />
                  <Input
                    placeholder="Search documents..."
                    value={searchTerm}
                    onChange={(e) => setSearchTerm(e.target.value)}
                    className="pl-10"
                  />
                </div>
              </div>
              
              <Select value={categoryFilter} onValueChange={setCategoryFilter}>
                <SelectTrigger className="w-48">
                  <SelectValue placeholder="Category" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">All Categories</SelectItem>
                  <SelectItem value="dissertation">Dissertation</SelectItem>
                  <SelectItem value="thesis">Thesis</SelectItem>
                  <SelectItem value="essay">Essay</SelectItem>
                  <SelectItem value="research_paper">Research Paper</SelectItem>
                  <SelectItem value="report">Report</SelectItem>
                </SelectContent>
              </Select>
              
              <Select value={statusFilter} onValueChange={setStatusFilter}>
                <SelectTrigger className="w-48">
                  <SelectValue placeholder="Status" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">All Status</SelectItem>
                  <SelectItem value="available">Available</SelectItem>
                  <SelectItem value="claimed">Claimed</SelectItem>
                  <SelectItem value="checking">Checking</SelectItem>
                  <SelectItem value="completed">Completed</SelectItem>
                  <SelectItem value="flagged">Flagged</SelectItem>
                </SelectContent>
              </Select>
              
              <Select value={sortBy} onValueChange={setSortBy}>
                <SelectTrigger className="w-48">
                  <SelectValue placeholder="Sort By" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="uploadedAt">Upload Time</SelectItem>
                  <SelectItem value="title">Title</SelectItem>
                  <SelectItem value="wordCount">Word Count</SelectItem>
                  <SelectItem value="priority">Priority</SelectItem>
                </SelectContent>
              </Select>
              
              <Button
                variant="outline"
                onClick={() => setSortOrder(sortOrder === 'asc' ? 'desc' : 'asc')}
              >
                {sortOrder === 'asc' ? '↑' : '↓'}
              </Button>
            </div>
          </CardContent>
        </Card>

        {/* Documents Table */}
        <Card>
          <CardHeader>
            <CardTitle>Documents Queue ({filteredDocuments.length})</CardTitle>
          </CardHeader>
          <CardContent>
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Title</TableHead>
                  <TableHead>Category</TableHead>
                  <TableHead>Words</TableHead>
                  <TableHead>Priority</TableHead>
                  <TableHead>Status</TableHead>
                  <TableHead>Uploaded</TableHead>
                  <TableHead>Scores</TableHead>
                  <TableHead>Loops</TableHead>
                  <TableHead>Actions</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {filteredDocuments.map((doc) => (
                  <TableRow key={doc.id} className="hover:bg-gray-50 dark:hover:bg-gray-800">
                    <TableCell className="max-w-xs">
                      <div className="truncate font-medium">{doc.title}</div>
                      <div className="text-sm text-gray-500">by {doc.uploadedBy}</div>
                    </TableCell>
                    <TableCell>
                      <Badge variant="outline" className="capitalize">
                        {doc.category.replace('_', ' ')}
                      </Badge>
                    </TableCell>
                    <TableCell>{doc.wordCount.toLocaleString()}</TableCell>
                    <TableCell>
                      <Badge className={getPriorityColor(doc.priority)}>
                        {doc.priority}
                      </Badge>
                    </TableCell>
                    <TableCell>
                      <span className={`font-medium ${getStatusColor(doc.status)}`}>
                        {doc.status}
                      </span>
                      {doc.claimedBy && (
                        <div className="text-xs text-gray-500">
                          by {doc.claimedBy}
                        </div>
                      )}
                    </TableCell>
                    <TableCell>
                      <div className="text-sm">
                        {formatTimeAgo(doc.uploadedAt)}
                      </div>
                      <div className="text-xs text-gray-500">
                        <Calendar className="w-3 h-3 inline mr-1" />
                        {new Date(doc.uploadedAt).toLocaleDateString()}
                      </div>
                    </TableCell>
                    <TableCell>
                      {doc.plagiarismScore !== undefined && doc.aiScore !== undefined ? (
                        <div className="text-sm">
                          <div className={`${doc.plagiarismScore <= 5 ? 'text-green-600' : 'text-red-600'}`}>
                            P: {doc.plagiarismScore}%
                          </div>
                          <div className={`${doc.aiScore === 0 ? 'text-green-600' : 'text-red-600'}`}>
                            AI: {doc.aiScore}%
                          </div>
                        </div>
                      ) : (
                        <span className="text-gray-400">Pending</span>
                      )}
                    </TableCell>
                    <TableCell>
                      <div className="text-sm">
                        {doc.loopCount}/{doc.maxLoops}
                        {doc.isZeroMarked && (
                          <Badge variant="secondary" className="ml-1 text-xs">
                            ZORO
                          </Badge>
                        )}
                      </div>
                    </TableCell>
                    <TableCell>
                      <div className="flex space-x-2">
                        {doc.status === 'available' && (
                          <Button
                            size="sm"
                            onClick={() => handleClaimDocument(doc.id)}
                            className="text-xs"
                          >
                            Claim
                          </Button>
                        )}
                        
                        {doc.claimedBy === user?.username && (
                          <>
                            <Button
                              size="sm"
                              variant="outline"
                              onClick={() => handleDownloadDocument(doc.id)}
                              className="text-xs"
                            >
                              <Download className="w-3 h-3" />
                            </Button>
                            
                            <Dialog open={showUploadDialog} onOpenChange={setShowUploadDialog}>
                              <DialogTrigger asChild>
                                <Button
                                  size="sm"
                                  variant="outline"
                                  onClick={() => setSelectedDocument(doc)}
                                  className="text-xs"
                                >
                                  <Upload className="w-3 h-3" />
                                </Button>
                              </DialogTrigger>
                              <DialogContent className="max-w-md">
                                <DialogHeader>
                                  <DialogTitle>Upload Reports</DialogTitle>
                                </DialogHeader>
                                <div className="space-y-4">
                                  <div>
                                    <label className="block text-sm font-medium mb-2">
                                      Plagiarism Report (PDF)
                                    </label>
                                    <Input
                                      type="file"
                                      accept=".pdf"
                                      onChange={(e) => setUploadFiles(prev => ({
                                        ...prev,
                                        plagiarismReport: e.target.files?.[0] || null
                                      }))}
                                    />
                                  </div>
                                  <div>
                                    <label className="block text-sm font-medium mb-2">
                                      AI Detection Report (PDF)
                                    </label>
                                    <Input
                                      type="file"
                                      accept=".pdf"
                                      onChange={(e) => setUploadFiles(prev => ({
                                        ...prev,
                                        aiReport: e.target.files?.[0] || null
                                      }))}
                                    />
                                  </div>
                                  <div className="flex space-x-2">
                                    <Button 
                                      onClick={() => selectedDocument && handleUploadReports(selectedDocument.id)}
                                      className="flex-1"
                                    >
                                      Upload Reports
                                    </Button>
                                    <Button
                                      variant="outline"
                                      onClick={() => selectedDocument && handleMarkZero(selectedDocument.id)}
                                    >
                                      Mark ZORO
                                    </Button>
                                  </div>
                                </div>
                              </DialogContent>
                            </Dialog>
                          </>
                        )}
                        
                        <Button
                          size="sm"
                          variant="ghost"
                          onClick={() => setSelectedDocument(doc)}
                          className="text-xs"
                        >
                          <Eye className="w-3 h-3" />
                        </Button>
                      </div>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
            
            {isLoadingDocuments ? (
              <div className="text-center py-8">
                <Loader2 className="w-6 h-6 animate-spin mx-auto mb-2 text-blue-600" />
                <p className="text-gray-500">Loading documents...</p>
              </div>
            ) : filteredDocuments.length === 0 ? (
              <div className="text-center py-8 text-gray-500">
                No documents found matching your criteria.
              </div>
            ) : null}
          </CardContent>
        </Card>
      </div>
    </div>
  );
}, ['document.claim']); // Require document claim permission