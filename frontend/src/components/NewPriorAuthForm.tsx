import React, { useState } from "react";
import { usePriorAuth } from "../context/PriorAuthContext";
import { XIcon } from "lucide-react";

interface NewPriorAuthFormProps {
  onClose: () => void;
}

const NewPriorAuthForm: React.FC<NewPriorAuthFormProps> = ({ onClose }) => {
  const { addPriorAuth, loading } = usePriorAuth();
  const [patientName, setPatientName] = useState("");
  const [procedure, setProcedure] = useState("");
  const [authDocumentFile, setAuthDocumentFile] = useState<File | null>(null);
  const [clinicalNotesFile, setClinicalNotesFile] = useState<File | null>(null);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!authDocumentFile || !clinicalNotesFile) {
      setError("Both PDF files are required");
      return;
    }

    try {
      setSubmitting(true);
      setError(null);

      await addPriorAuth({
        patient_name: patientName,
        procedure,
        authDocumentFile,
        clinicalNotesFile,
      });

      onClose();
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : "Failed to create prior authorization"
      );
    } finally {
      setSubmitting(false);
    }
  };

  const validateFile = (file: File): string | null => {
    if (file.type !== "application/pdf") {
      return "Only PDF files are allowed";
    }
    if (file.size > 10 * 1024 * 1024) {
      // 10MB
      return "File size must be less than 10MB";
    }
    return null;
  };

  const handleAuthDocumentChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      const error = validateFile(file);
      if (error) {
        setError(error);
        e.target.value = "";
        return;
      }
      setAuthDocumentFile(file);
      setError(null);
    }
  };

  const handleClinicalNotesChange = (
    e: React.ChangeEvent<HTMLInputElement>
  ) => {
    const file = e.target.files?.[0];
    if (file) {
      const error = validateFile(file);
      if (error) {
        setError(error);
        e.target.value = "";
        return;
      }
      setClinicalNotesFile(file);
      setError(null);
    }
  };

  return (
    <div className="fixed inset-0 bg-gray-500 bg-opacity-75 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg shadow-xl max-w-md w-full p-6">
        <div className="flex justify-between items-center mb-4">
          <h3 className="text-lg font-medium text-gray-900">
            New Prior Authorization
          </h3>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-gray-500"
            disabled={submitting}
          >
            <XIcon className="h-5 w-5" />
          </button>
        </div>

        {error && (
          <div className="mb-4 p-3 bg-red-100 border border-red-300 rounded-md">
            <p className="text-sm text-red-700">{error}</p>
          </div>
        )}

        <form onSubmit={handleSubmit}>
          <div className="space-y-4">
            <div>
              <label
                htmlFor="patientName"
                className="block text-sm font-medium text-gray-700"
              >
                Patient Name
              </label>
              <input
                type="text"
                id="patientName"
                value={patientName}
                onChange={(e) => setPatientName(e.target.value)}
                className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
                required
                disabled={submitting}
              />
            </div>

            <div>
              <label
                htmlFor="procedure"
                className="block text-sm font-medium text-gray-700"
              >
                Procedure Name
              </label>
              <input
                type="text"
                id="procedure"
                value={procedure}
                onChange={(e) => setProcedure(e.target.value)}
                className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
                required
                disabled={submitting}
              />
            </div>

            <div>
              <label
                htmlFor="authDocument"
                className="block text-sm font-medium text-gray-700"
              >
                Prior Authorization Document (PDF)
              </label>
              <input
                type="file"
                id="authDocument"
                accept="application/pdf"
                onChange={handleAuthDocumentChange}
                className="mt-1 block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-md file:border-0 file:text-sm file:font-semibold file:bg-blue-50 file:text-blue-700 hover:file:bg-blue-100"
                required
                disabled={submitting}
              />
              {authDocumentFile && (
                <p className="mt-1 text-xs text-green-600">
                  Selected: {authDocumentFile.name}
                </p>
              )}
            </div>

            <div>
              <label
                htmlFor="clinicalNotes"
                className="block text-sm font-medium text-gray-700"
              >
                Clinical Notes (PDF)
              </label>
              <input
                type="file"
                id="clinicalNotes"
                accept="application/pdf"
                onChange={handleClinicalNotesChange}
                className="mt-1 block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-md file:border-0 file:text-sm file:font-semibold file:bg-blue-50 file:text-blue-700 hover:file:bg-blue-100"
                required
                disabled={submitting}
              />
              {clinicalNotesFile && (
                <p className="mt-1 text-xs text-green-600">
                  Selected: {clinicalNotesFile.name}
                </p>
              )}
            </div>
          </div>

          <div className="mt-5 sm:mt-6 sm:grid sm:grid-cols-2 sm:gap-3 sm:grid-flow-row-dense">
            <button
              type="submit"
              disabled={submitting || loading}
              className="w-full inline-flex justify-center rounded-md border border-transparent shadow-sm px-4 py-2 bg-blue-600 text-base font-medium text-white hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 sm:col-start-2 sm:text-sm disabled:bg-gray-400 disabled:cursor-not-allowed"
            >
              {submitting ? "Creating..." : "Submit"}
            </button>
            <button
              type="button"
              onClick={onClose}
              disabled={submitting}
              className="mt-3 w-full inline-flex justify-center rounded-md border border-gray-300 shadow-sm px-4 py-2 bg-white text-base font-medium text-gray-700 hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 sm:mt-0 sm:col-start-1 sm:text-sm disabled:bg-gray-100 disabled:cursor-not-allowed"
            >
              Cancel
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default NewPriorAuthForm;
