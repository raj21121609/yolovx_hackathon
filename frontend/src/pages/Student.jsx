import React, { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import { ArrowLeft, User, Activity, Clock } from 'lucide-react';
import { reportService } from '../services/reportService';
import studentService from '../services/studentService';

const Student = () => {
  const { id } = useParams();
  const [student, setStudent] = useState(null);
  const [analytics, setAnalytics] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchStudentData = async () => {
      try {
        const studentData = await studentService.getAll();
        const found = studentData.find(s => s.id === id);
        setStudent(found);
        
        const analyticsData = await reportService.getStudentAnalytics(id);
        setAnalytics(analyticsData);
      } catch (err) {
        console.error("Failed to fetch student details", err);
      } finally {
        setLoading(false);
      }
    };
    
    fetchStudentData();
  }, [id]);

  if (loading) return <div className="p-8">Loading student details...</div>;
  if (!student) return <div className="p-8 text-red-500">Student not found</div>;

  return (
    <div className="p-8 max-w-7xl mx-auto space-y-8">
      <div>
        <Link to="/students" className="text-indigo-600 hover:text-indigo-800 flex items-center text-sm font-medium mb-4">
          <ArrowLeft size={16} className="mr-1" /> Back to Students
        </Link>
        <div className="flex items-center space-x-4">
          <div className="w-16 h-16 rounded-full bg-indigo-100 text-indigo-700 flex items-center justify-center font-bold text-2xl">
            {student.name.charAt(0)}
          </div>
          <div>
            <h1 className="text-3xl font-bold text-gray-900">{student.name}</h1>
            <p className="text-gray-500">{student.roll_number} • {student.department}</p>
          </div>
        </div>
      </div>

      {analytics && (
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
          <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-100 flex items-center space-x-4">
            <div className="p-3 bg-blue-100 text-blue-600 rounded-lg">
              <Activity size={24} />
            </div>
            <div>
              <p className="text-sm text-gray-500 font-medium">Total Sessions</p>
              <p className="text-2xl font-bold text-gray-900">{analytics.total_sessions}</p>
            </div>
          </div>
          <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-100 flex items-center space-x-4">
            <div className="p-3 bg-green-100 text-green-600 rounded-lg">
              <User size={24} />
            </div>
            <div>
              <p className="text-sm text-gray-500 font-medium">Present</p>
              <p className="text-2xl font-bold text-gray-900">{analytics.present}</p>
            </div>
          </div>
          <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-100 flex items-center space-x-4">
            <div className="p-3 bg-yellow-100 text-yellow-600 rounded-lg">
              <Clock size={24} />
            </div>
            <div>
              <p className="text-sm text-gray-500 font-medium">Late</p>
              <p className="text-2xl font-bold text-gray-900">{analytics.late}</p>
            </div>
          </div>
          <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-100 flex items-center space-x-4">
            <div className="p-3 bg-indigo-100 text-indigo-600 rounded-lg">
              <Activity size={24} />
            </div>
            <div>
              <p className="text-sm text-gray-500 font-medium">Attendance %</p>
              <p className="text-2xl font-bold text-gray-900">{analytics.attendance_percentage}%</p>
            </div>
          </div>
        </div>
      )}

      <div className="bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden p-6">
        <h2 className="text-lg font-bold text-gray-900 mb-4">View History</h2>
        <p className="text-gray-500 text-sm mb-4">
          To see a detailed breakdown of attendance history for {student.name}, please visit the main reports page.
        </p>
        <Link to={`/reports`} className="px-4 py-2 bg-indigo-600 text-white rounded-lg text-sm font-medium hover:bg-indigo-700 inline-block">
          Open Reports Dashboard
        </Link>
      </div>
    </div>
  );
};

export default Student;
