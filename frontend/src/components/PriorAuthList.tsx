import React, { useState } from "react";
import { Link } from "react-router-dom";
import { usePriorAuth } from "../context/PriorAuthContext";
import NewPriorAuthForm from "./NewPriorAuthForm";
import { PlusIcon, RefreshCwIcon } from "lucide-react";

const PriorAuthList: React.FC = () => {
  const { priorAuths, loading, error, refreshPriorAuths } = usePriorAuth();
  const [isFormOpen, setIsFormOpen] = useState(false);

  const handleRefresh = async () => {
    try {
      await refreshPriorAuths();
    } catch (err) {
      console.error("Failed to refresh:", err);
    }
  };

  const formatDate = (dateString: string) => {
    try {
      return new Date(dateString).toLocaleDateString();
    } catch {
      return dateString;
    }
  };

  return (
    <div className="bg-white shadow rounded-lg">
      <div className="px-4 py-5 sm:px-6 flex justify-between items-center">
        <div>
          <h2 className="text-lg font-medium text-gray-900">
            Prior Authorizations
          </h2>
          {error && <p className="mt-1 text-sm text-red-600">{error}</p>}
        </div>
        <div className="flex space-x-2">
          <button
            onClick={handleRefresh}
            disabled={loading}
            className="inline-flex items-center px-3 py-2 border border-gray-300 text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50"
          >
            <RefreshCwIcon
              className={`h-4 w-4 mr-1 ${loading ? "animate-spin" : ""}`}
            />
            Refresh
          </button>
          <button
            onClick={() => setIsFormOpen(true)}
            disabled={loading}
            className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50"
          >
            <PlusIcon className="h-5 w-5 mr-2" />
            New
          </button>
        </div>
      </div>

      <div className="border-t border-gray-200">
        {loading && priorAuths.length === 0 ? (
          <div className="px-6 py-12 text-center">
            <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
            <p className="mt-2 text-sm text-gray-500">
              Loading prior authorizations...
            </p>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th
                    scope="col"
                    className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"
                  >
                    Patient Name
                  </th>
                  <th
                    scope="col"
                    className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"
                  >
                    Date
                  </th>
                  <th
                    scope="col"
                    className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"
                  >
                    Procedure
                  </th>
                  <th
                    scope="col"
                    className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"
                  >
                    Status
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {priorAuths.map((auth) => (
                  <tr key={auth.id} className="hover:bg-gray-50 cursor-pointer">
                    <td className="px-6 py-4 whitespace-nowrap">
                      <Link
                        to={`/details/${auth.id}`}
                        className="text-blue-600 hover:text-blue-900 block"
                      >
                        {auth.patient_name}
                      </Link>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <Link
                        to={`/details/${auth.id}`}
                        className="text-gray-900 block"
                      >
                        {formatDate(auth.date)}
                      </Link>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <Link
                        to={`/details/${auth.id}`}
                        className="text-gray-900 block"
                      >
                        {auth.procedure}
                      </Link>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <Link to={`/details/${auth.id}`} className="block">
                        <span
                          className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${
                            auth.status === "approved"
                              ? "bg-green-100 text-green-800"
                              : auth.status === "denied"
                              ? "bg-red-100 text-red-800"
                              : "bg-yellow-100 text-yellow-800"
                          }`}
                        >
                          {auth.status}
                        </span>
                      </Link>
                    </td>
                  </tr>
                ))}
                {priorAuths.length === 0 && !loading && (
                  <tr>
                    <td
                      colSpan={4}
                      className="px-6 py-12 text-center text-gray-500"
                    >
                      No prior authorizations found. Create a new one to get
                      started.
                    </td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {isFormOpen && <NewPriorAuthForm onClose={() => setIsFormOpen(false)} />}
    </div>
  );
};

export default PriorAuthList;
