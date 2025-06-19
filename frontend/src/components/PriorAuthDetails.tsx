import React, { useState, useEffect } from "react";
import { useParams, Link } from "react-router-dom";
import { usePriorAuth } from "../context/PriorAuthContext";
import { apiClient } from "../config/api";
import PDFViewer from "./PDFViewer";
import MedicalNecessityQuestions from "./MedicalNecessityQuestions";
import { ArrowLeftIcon } from "lucide-react";

// Sample medical necessity questions (in a real app, this would come from the backend)
const sampleQuestions = [
  {
    id: "1",
    category: "Patient History",
    question:
      "Has the patient tried conservative treatment for at least 6 weeks?",
    answer: "Yes",
  },
  {
    id: "2",
    category: "Patient History",
    question: "Are there any documented physical therapy sessions?",
    answer: "Yes - 12 sessions completed",
  },
  {
    id: "3",
    category: "Current Symptoms",
    question: "Is there presence of neurological symptoms?",
    answer: "Yes - Radiating pain down left leg",
  },
  {
    id: "4",
    category: "Current Symptoms",
    question: "Pain level on a scale of 1-10?",
    answer: "8/10",
  },
  {
    id: "5",
    category: "Imaging",
    question: "Has an X-ray been performed in the last 3 months?",
    answer: "Yes - Dated 2023-10-15",
  },
];

type ViewMode = "questions" | "pdf";

const PriorAuthDetails: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const { getPriorAuth, loading } = usePriorAuth();
  const [viewMode, setViewMode] = useState<ViewMode>("questions");
  const [priorAuth, setPriorAuth] = useState(getPriorAuth(id || ""));
  const [detailsLoading, setDetailsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Fetch detailed data from API if not in context
  useEffect(() => {
    const fetchDetails = async () => {
      if (!id) return;

      const contextAuth = getPriorAuth(id);
      if (contextAuth) {
        setPriorAuth(contextAuth);
        return;
      }

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

    fetchDetails();
  }, [id, getPriorAuth]);

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
                Medical Necessity
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
              <MedicalNecessityQuestions questions={sampleQuestions} />
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
