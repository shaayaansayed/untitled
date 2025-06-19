import React from 'react';
interface Question {
  id: string;
  question: string;
  answer?: string;
  category: string;
}
interface MedicalNecessityQuestionsProps {
  questions: Question[];
}
const MedicalNecessityQuestions: React.FC<MedicalNecessityQuestionsProps> = ({
  questions
}) => {
  const categories = Array.from(new Set(questions.map(q => q.category)));
  return <div className="h-full overflow-auto bg-white">
      <div className="px-4 py-5 sm:px-6">
        <h3 className="text-lg font-medium leading-6 text-gray-900">
          Medical Necessity Questions
        </h3>
        <p className="mt-1 text-sm text-gray-500">
          Questions extracted from the prior authorization document
        </p>
      </div>
      <div className="border-t border-gray-200 px-4 py-5 sm:px-6">
        {categories.map(category => <div key={category} className="mb-8">
            <h4 className="text-md font-medium text-gray-900 mb-4">
              {category}
            </h4>
            <div className="space-y-6">
              {questions.filter(q => q.category === category).map(question => <div key={question.id} className="bg-gray-50 rounded-lg p-4 border border-gray-200">
                    <p className="text-sm text-gray-900 font-medium mb-2">
                      {question.question}
                    </p>
                    {question.answer && <p className="text-sm text-gray-600">
                        Answer: {question.answer}
                      </p>}
                  </div>)}
            </div>
          </div>)}
      </div>
    </div>;
};
export default MedicalNecessityQuestions;