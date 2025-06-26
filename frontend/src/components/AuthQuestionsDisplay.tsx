import React from "react";
import { Tree } from "antd";
import type { TreeDataNode } from "antd";
import {
  CheckCircleOutlined,
  CloseCircleOutlined,
  ClockCircleOutlined,
  DownOutlined,
} from "@ant-design/icons";
import type { AuthQuestion, AuthCriterion, AuthOperation } from "../config/api";

interface AuthQuestionsDisplayProps {
  authQuestions?: AuthQuestion;
}

const AuthQuestionsDisplay: React.FC<AuthQuestionsDisplayProps> = ({
  authQuestions,
}) => {
  // Transform auth questions data to TreeDataNode format
  const transformToTreeData = (question: AuthQuestion): TreeDataNode => {
    if (question.type === "criterion") {
      const criterion = question as AuthCriterion;

      // Determine icon based on value - FIXED: Check is_met property
      let icon;
      let titleColor = "";

      // Handle both old format (boolean) and new format (object with is_met)
      const isMet =
        typeof criterion.value === "boolean"
          ? criterion.value
          : criterion.value?.is_met;

      if (isMet === true) {
        icon = <CheckCircleOutlined style={{ color: "#52c41a" }} />;
        titleColor = "text-green-700";
      } else if (isMet === false) {
        icon = <CloseCircleOutlined style={{ color: "#ff4d4f" }} />;
        titleColor = "text-red-700";
      } else {
        icon = <ClockCircleOutlined style={{ color: "#d9d9d9" }} />;
        titleColor = "text-gray-500";
      }

      return {
        key: criterion.id,
        title: (
          <span className={`flex items-center gap-2 ${titleColor}`}>
            {icon}
            <span>{criterion.description}</span>
            {/* Optional: Show justification on hover or as subtitle */}
            {criterion.value &&
              typeof criterion.value === "object" &&
              criterion.value.justification && (
                <span
                  className="text-xs text-gray-400 ml-2"
                  title={criterion.value.justification}
                >
                  ({criterion.value.answer})
                </span>
              )}
          </span>
        ),
        isLeaf: true,
      };
    }

    // Handle operation type
    const operation = question as AuthOperation;
    const children =
      operation.children?.map((child) => transformToTreeData(child)) || [];

    return {
      key: operation.id,
      title: (
        <span className="flex items-center gap-2">
          <span className="bg-blue-100 text-blue-800 text-xs font-bold px-2 py-1 rounded uppercase">
            {operation.operator}
          </span>
          <span className="font-medium text-blue-900">
            {operation.description}
          </span>
        </span>
      ),
      children: children,
    };
  };

  // Count criteria and check completion status - FIXED: Check is_met property
  const countStats = (
    question: AuthQuestion
  ): { total: number; completed: number; met: number } => {
    if (question.type === "criterion") {
      const hasValue = question.value !== null && question.value !== undefined;
      const completed = hasValue ? 1 : 0;

      // Handle both old format (boolean) and new format (object with is_met)
      let isMet = false;
      if (typeof question.value === "boolean") {
        isMet = question.value;
      } else if (question.value && typeof question.value === "object") {
        isMet = question.value.is_met === true;
      }

      const met = isMet ? 1 : 0;
      return { total: 1, completed, met };
    }

    const childStats =
      question.children?.map((child) => countStats(child)) || [];
    return childStats.reduce(
      (acc, stats) => ({
        total: acc.total + stats.total,
        completed: acc.completed + stats.completed,
        met: acc.met + stats.met,
      }),
      { total: 0, completed: 0, met: 0 }
    );
  };

  if (!authQuestions) {
    return (
      <div className="h-full overflow-auto bg-white">
        <div className="px-4 py-5 sm:px-6">
          <h3 className="text-lg font-medium leading-6 text-gray-900">
            Authorization Criteria
          </h3>
          <p className="mt-1 text-sm text-gray-500">
            No authorization criteria available yet
          </p>
        </div>
        <div className="border-t border-gray-200 px-4 py-8">
          <div className="text-center">
            <ClockCircleOutlined className="text-4xl text-gray-400" />
            <h3 className="mt-2 text-sm font-medium text-gray-900">
              Processing Document
            </h3>
            <p className="mt-1 text-sm text-gray-500">
              The authorization criteria are being extracted from the uploaded
              document. This may take a few moments.
            </p>
          </div>
        </div>
      </div>
    );
  }

  const stats = countStats(authQuestions);
  const completionRate =
    stats.total > 0 ? Math.round((stats.completed / stats.total) * 100) : 0;

  const treeData = [transformToTreeData(authQuestions)];

  return (
    <div className="h-full overflow-auto bg-white">
      <div className="px-4 py-5 sm:px-6">
        <h3 className="text-lg font-medium leading-6 text-gray-900">
          Authorization Criteria
        </h3>
        <div className="mt-2 flex items-center space-x-4 text-sm text-gray-500">
          <span>{stats.total} total criteria</span>
          <span>•</span>
          <span>{stats.completed} reviewed</span>
          <span>•</span>
          <span className="text-green-600">{stats.met} met</span>
          {completionRate > 0 && (
            <>
              <span>•</span>
              <span>{completionRate}% complete</span>
            </>
          )}
        </div>

        {/* Main title from the root description */}
        {authQuestions.description && (
          <div className="mt-3 p-3 bg-blue-50 rounded-lg border border-blue-200">
            <h4 className="text-sm font-medium text-blue-900">
              {authQuestions.description}
            </h4>
          </div>
        )}
      </div>

      <div className="border-t border-gray-200 px-4 py-5 sm:px-6">
        <Tree
          showLine
          switcherIcon={<DownOutlined />}
          defaultExpandAll
          treeData={treeData}
          className="bg-white"
        />
      </div>
    </div>
  );
};

export default AuthQuestionsDisplay;
