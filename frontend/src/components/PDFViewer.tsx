import React from 'react';
interface PDFViewerProps {
  fileUrl: string;
  title: string;
}
const PDFViewer: React.FC<PDFViewerProps> = ({
  fileUrl,
  title
}) => {
  return <div className="flex flex-col h-full">
      <div className="bg-gray-100 px-4 py-2 border-b">
        <h3 className="text-sm font-medium text-gray-700">{title}</h3>
      </div>
      <div className="flex-1 bg-gray-50">
        <iframe src={fileUrl} className="w-full h-full" title={title} />
      </div>
    </div>;
};
export default PDFViewer;