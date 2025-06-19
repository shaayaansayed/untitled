import React, { useState, createContext, useContext, useEffect } from "react";
import { apiClient } from "../config/api";
import type { PriorAuth, CreatePriorAuthRequest } from "../config/api";

export interface PriorAuthContextType {
  priorAuths: PriorAuth[];
  loading: boolean;
  error: string | null;
  addPriorAuth: (
    auth: Omit<
      CreatePriorAuthRequest,
      "auth_document_id" | "clinical_notes_id"
    > & {
      authDocumentFile: File;
      clinicalNotesFile: File;
    }
  ) => Promise<void>;
  getPriorAuth: (id: string) => PriorAuth | undefined;
  refreshPriorAuths: () => Promise<void>;
  deletePriorAuth: (id: string) => Promise<void>;
}

const PriorAuthContext = createContext<PriorAuthContextType | undefined>(
  undefined
);

export const usePriorAuth = () => {
  const context = useContext(PriorAuthContext);
  if (!context) {
    throw new Error("usePriorAuth must be used within a PriorAuthProvider");
  }
  return context;
};

export const PriorAuthProvider: React.FC<{
  children: React.ReactNode;
}> = ({ children }) => {
  const [priorAuths, setPriorAuths] = useState<PriorAuth[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const refreshPriorAuths = async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await apiClient.getPriorAuthorizations();
      setPriorAuths(data);
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : "Failed to load prior authorizations"
      );
      console.error("Error fetching prior authorizations:", err);
    } finally {
      setLoading(false);
    }
  };

  const addPriorAuth = async (
    auth: Omit<
      CreatePriorAuthRequest,
      "auth_document_id" | "clinical_notes_id"
    > & {
      authDocumentFile: File;
      clinicalNotesFile: File;
    }
  ) => {
    try {
      setLoading(true);
      setError(null);

      // Upload both files first
      const [authDocUpload, clinicalNotesUpload] = await Promise.all([
        apiClient.uploadFile(auth.authDocumentFile, "prior_authorization"),
        apiClient.uploadFile(auth.clinicalNotesFile, "clinical_notes"),
      ]);

      // Create the prior authorization with the uploaded file IDs
      const newPriorAuth = await apiClient.createPriorAuthorization({
        patient_name: auth.patient_name,
        procedure: auth.procedure,
        auth_document_id: authDocUpload.id,
        clinical_notes_id: clinicalNotesUpload.id,
      });

      // Refresh the list to get the latest data
      await refreshPriorAuths();
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : "Failed to create prior authorization"
      );
      throw err; // Re-throw so the form can handle it
    } finally {
      setLoading(false);
    }
  };

  const deletePriorAuth = async (id: string) => {
    try {
      setLoading(true);
      setError(null);
      await apiClient.deletePriorAuthorization(id);
      await refreshPriorAuths();
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : "Failed to delete prior authorization"
      );
      throw err;
    } finally {
      setLoading(false);
    }
  };

  const getPriorAuth = (id: string) => {
    return priorAuths.find((auth) => auth.id === id);
  };

  // Load initial data
  useEffect(() => {
    refreshPriorAuths();
  }, []);

  return (
    <PriorAuthContext.Provider
      value={{
        priorAuths,
        loading,
        error,
        addPriorAuth,
        getPriorAuth,
        refreshPriorAuths,
        deletePriorAuth,
      }}
    >
      {children}
    </PriorAuthContext.Provider>
  );
};
