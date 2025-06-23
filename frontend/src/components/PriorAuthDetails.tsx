import React, { useState, useEffect } from "react";
import { useParams, Link } from "react-router-dom";
import { usePriorAuth } from "../context/PriorAuthContext";
import { apiClient } from "../config/api";
import PDFViewer from "./PDFViewer";
import AuthQuestionsDisplay from "./AuthQuestionsDisplay";
import { ArrowLeftIcon, RefreshCwIcon } from "lucide-react";

type ViewMode = "questions" | "pdf";

const PriorAuthDetails: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const { getPriorAuth, loading } = usePriorAuth();
  const [viewMode, setViewMode] = useState<ViewMode>("questions");
  const [priorAuth, setPriorAuth] = useState(getPriorAuth(id || ""));
  const [detailsLoading, setDetailsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [refreshing, setRefreshing] = useState(false);

  // Fetch detailed data from API
  const fetchDetails = async () => {
    if (!id) return;

    try {
      setDetailsLoading(true);
      setError(null);
      const detailedAuth = await apiClient.getPriorAuthorization(id);
      setPriorAuth(detailedAuth);
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : "Failed to load prior authorization details"
      );
    } finally {
      setDetailsLoading(false);
    }
  };

  // Initial load
  useEffect(() => {
    const contextAuth = getPriorAuth(id || "");
    if (contextAuth) {
      setPriorAuth(contextAuth);
    }

    // Always fetch fresh data from API to get latest auth_questions
    fetchDetails();
  }, [id, getPriorAuth]);

  // Refresh data
  const handleRefresh = async () => {
    setRefreshing(true);
    await fetchDetails();
    setRefreshing(false);
  };

  const formatDate = (dateString: string) => {
    try {
      return new Date(dateString).toLocaleDateString();
    } catch {
      return dateString;
    }
  };

  const getFileUrl = (fileId: string) => {
    return apiClient.getFileUrl(fileId);
  };

  if (loading || detailsLoading) {
    return (
      <div className="text-center py-10">
        <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
        <h2 className="mt-4 text-xl font-medium text-gray-900">Loading...</h2>
      </div>
    );
  }

  if (error) {
    return (
      <div className="text-center py-10">
        <h2 className="text-xl font-medium text-gray-900">Error</h2>
        <p className="mt-2 text-red-600">{error}</p>
        <div className="mt-4">
          <Link to="/" className="text-blue-600 hover:text-blue-800">
            Return to list
          </Link>
        </div>
      </div>
    );
  }

  if (!priorAuth) {
    return (
      <div className="text-center py-10">
        <h2 className="text-xl font-medium text-gray-900">
          Prior authorization not found
        </h2>
        <div className="mt-4">
          <Link to="/" className="text-blue-600 hover:text-blue-800">
            Return to list
          </Link>
        </div>
      </div>
    );
  }

  return (
    <div className="bg-white shadow rounded-lg">
      <div className="px-4 py-5 sm:px-6 flex justify-between items-center border-b border-gray-200">
        <div>
          <Link
            to="/"
            className="flex items-center text-blue-600 hover:text-blue-800 mb-2"
          >
            <ArrowLeftIcon className="h-4 w-4 mr-1" />
            Back to list
          </Link>
          <h2 className="text-lg font-medium text-gray-900">
            {priorAuth.patient_name}
          </h2>
          <p className="text-sm text-gray-500">
            {priorAuth.procedure} • {formatDate(priorAuth.date)}
            <span
              className={`ml-2 inline-flex px-2 py-1 text-xs font-semibold rounded-full ${
                priorAuth.status === "approved"
                  ? "bg-green-100 text-green-800"
                  : priorAuth.status === "denied"
                  ? "bg-red-100 text-red-800"
                  : "bg-yellow-100 text-yellow-800"
              }`}
            >
              {priorAuth.status}
            </span>
          </p>
        </div>

        <button
          onClick={handleRefresh}
          disabled={refreshing}
          className="inline-flex items-center px-3 py-2 border border-gray-300 text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50"
        >
          <RefreshCwIcon
            className={`h-4 w-4 mr-1 ${refreshing ? "animate-spin" : ""}`}
          />
          Refresh
        </button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4 h-[70vh] p-4">
        <div className="h-full border border-gray-200 rounded-md overflow-hidden">
          {priorAuth.clinical_notes ? (
            <PDFViewer
              fileUrl={getFileUrl(priorAuth.clinical_notes.id)}
              title="Clinical Notes"
            />
          ) : (
            <div className="flex items-center justify-center h-full bg-gray-50">
              <p className="text-gray-500">No clinical notes available</p>
            </div>
          )}
        </div>

        <div className="h-full border border-gray-200 rounded-md overflow-hidden flex flex-col">
          <div className="border-b border-gray-200">
            <nav className="flex" aria-label="Tabs">
              <button
                onClick={() => setViewMode("questions")}
                className={`px-4 py-2 text-sm font-medium flex-1 ${
                  viewMode === "questions"
                    ? "border-b-2 border-blue-500 text-blue-600"
                    : "text-gray-500 hover:text-gray-700"
                }`}
              >
                Authorization Criteria
              </button>
              <button
                onClick={() => setViewMode("pdf")}
                className={`px-4 py-2 text-sm font-medium flex-1 ${
                  viewMode === "pdf"
                    ? "border-b-2 border-blue-500 text-blue-600"
                    : "text-gray-500 hover:text-gray-700"
                }`}
              >
                Original Document
              </button>
            </nav>
          </div>
          <div className="flex-1">
            {viewMode === "questions" ? (
              <AuthQuestionsDisplay authQuestions={priorAuth.auth_questions} />
            ) : priorAuth.auth_document ? (
              <PDFViewer
                fileUrl={getFileUrl(priorAuth.auth_document.id)}
                title="Prior Authorization Document"
              />
            ) : (
              <div className="flex items-center justify-center h-full bg-gray-50">
                <p className="text-gray-500">
                  No authorization document available
                </p>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default PriorAuthDetails;
