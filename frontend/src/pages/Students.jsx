import { useState, useEffect } from 'react';
import studentService from '../services/studentService';
import { UserPlus, Upload, CheckCircle, XCircle } from 'lucide-react';

const Students = () => {
  const [students, setStudents] = useState([]);
  const [loading, setLoading] = useState(true);
  const [isModalOpen, setIsModalOpen] = useState(false);
  
  // Registration Flow State
  const [step, setStep] = useState(1); // 1: Details, 2: Upload Images, 3: Registering, 4: Result
  const [formData, setFormData] = useState({ name: '', roll_number: '', department: '' });
  const [studentId, setStudentId] = useState(null);
  const [selectedFiles, setSelectedFiles] = useState([]);
  const [regResult, setRegResult] = useState(null);

  const fetchStudents = async () => {
    try {
      const data = await studentService.getAll();
      setStudents(data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchStudents();
  }, []);

  const handleCreateStudent = async (e) => {
    e.preventDefault();
    try {
      const res = await studentService.create(formData);
      setStudentId(res.id);
      setStep(2); // Move to image upload
      fetchStudents();
    } catch (err) {
      console.error(err);
      alert("Failed to create student. Check if roll number is unique.");
    }
  };

  const handleFileChange = (e) => {
    const files = Array.from(e.target.files);
    if (files.length > 5) {
      alert("Please select exactly 5 images");
      return;
    }
    setSelectedFiles(files);
  };

  const handleRegisterFace = async () => {
    if (selectedFiles.length !== 5) {
      alert("Please provide exactly 5 images of the student.");
      return;
    }
    setStep(3); // Registering state
    
    const fd = new FormData();
    selectedFiles.forEach(f => fd.append('images', f));
    
    try {
      const res = await studentService.registerFace(studentId, fd);
      setRegResult({ success: true, ...res });
      setStep(4);
      fetchStudents();
    } catch (err) {
      setRegResult({ success: false, error: err.response?.data?.error || "Registration failed" });
      setStep(4);
    }
  };

  const resetModal = () => {
    setIsModalOpen(false);
    setStep(1);
    setFormData({ name: '', roll_number: '', department: '' });
    setStudentId(null);
    setSelectedFiles([]);
    setRegResult(null);
  };

  return (
    <div className="p-8 max-w-7xl mx-auto">
      <div className="flex justify-between items-center mb-8 border-b border-gray-200 pb-2">
        <h1 className="text-3xl font-extrabold text-sj-primary tracking-tight">Students Directory</h1>
        <button
          onClick={() => setIsModalOpen(true)}
          className="flex items-center gap-2 px-4 py-2 bg-sj-primary text-white rounded-lg text-sm font-medium hover:bg-sj-primary/90 shadow-sm transition-all"
        >
          <UserPlus size={18} /> Add Student
        </button>
      </div>

      {isModalOpen && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white p-6 rounded-xl w-full max-w-md shadow-lg">
            
            {step === 1 && (
              <>
                <h2 className="text-xl font-bold mb-4">Add New Student</h2>
                <form onSubmit={handleCreateStudent}>
                  <div className="mb-4">
                    <label className="block text-sm font-medium text-gray-700 mb-1">Name</label>
                    <input type="text" required value={formData.name} onChange={e => setFormData({...formData, name: e.target.value})} className="w-full border border-gray-300 rounded-lg p-2" />
                  </div>
                  <div className="mb-4">
                    <label className="block text-sm font-medium text-gray-700 mb-1">Roll Number</label>
                    <input type="text" required value={formData.roll_number} onChange={e => setFormData({...formData, roll_number: e.target.value})} className="w-full border border-gray-300 rounded-lg p-2" />
                  </div>
                  <div className="mb-6">
                    <label className="block text-sm font-medium text-gray-700 mb-1">Department</label>
                    <input type="text" required value={formData.department} onChange={e => setFormData({...formData, department: e.target.value})} className="w-full border border-gray-300 rounded-lg p-2" />
                  </div>
                  <div className="flex justify-end space-x-3">
                    <button type="button" onClick={resetModal} className="px-4 py-2 text-gray-600 hover:bg-gray-100 rounded-lg">Cancel</button>
                    <button type="submit" className="px-4 py-2 bg-sj-primary text-white rounded-lg hover:bg-sj-primary/90 shadow-sm transition-all">Next: Register Face</button>
                  </div>
                </form>
              </>
            )}

            {step === 2 && (
              <>
                <h2 className="text-xl font-bold mb-4">Register Face</h2>
                <p className="text-sm text-gray-600 mb-4">
                  Please provide exactly 5 clear front-facing images of the student in different lighting or angles.
                </p>
                <div className="mb-6">
                  <label className="block border-2 border-dashed border-gray-300 rounded-lg p-6 text-center cursor-pointer hover:bg-gray-50">
                    <Upload className="mx-auto h-12 w-12 text-gray-400" />
                    <span className="mt-2 block text-sm font-medium text-gray-900">
                      Select Images ({selectedFiles.length}/5 selected)
                    </span>
                    <input type="file" multiple accept="image/jpeg, image/png" className="hidden" onChange={handleFileChange} />
                  </label>
                </div>
                <div className="flex justify-end space-x-3">
                  <button type="button" onClick={resetModal} className="px-4 py-2 text-gray-600 hover:bg-gray-100 rounded-lg">Cancel</button>
                  <button 
                    onClick={handleRegisterFace}
                    disabled={selectedFiles.length !== 5}
                    className="px-4 py-2 bg-sj-primary text-white rounded-lg hover:bg-sj-primary/90 shadow-sm disabled:opacity-50 transition-all"
                  >
                    Upload & Register
                  </button>
                </div>
              </>
            )}

            {step === 3 && (
              <div className="text-center py-8">
                <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-sj-primary mx-auto mb-4"></div>
                <h2 className="text-xl font-bold text-gray-900">Registering face...</h2>
                <p className="text-gray-500 mt-2">Processing 5 images and extracting embeddings.</p>
              </div>
            )}

            {step === 4 && regResult && (
              <div className="text-center py-6">
                {regResult.success ? (
                  <>
                    <CheckCircle className="mx-auto h-16 w-16 text-green-500 mb-4" />
                    <h2 className="text-2xl font-bold text-gray-900">Face registered successfully</h2>
                    <p className="text-gray-500 mt-2">Samples processed: {regResult.samples_processed}/5</p>
                  </>
                ) : (
                  <>
                    <XCircle className="mx-auto h-16 w-16 text-red-500 mb-4" />
                    <h2 className="text-2xl font-bold text-gray-900">Registration Failed</h2>
                    <p className="text-red-600 mt-2">{JSON.stringify(regResult.error)}</p>
                  </>
                )}
                <button onClick={resetModal} className="mt-8 px-6 py-2 bg-gray-900 text-white rounded-lg hover:bg-gray-800">
                  Close
                </button>
              </div>
            )}

          </div>
        </div>
      )}

      <div className="bg-white rounded-xl shadow-md border border-gray-200/60 overflow-hidden">
        <table className="min-w-full divide-y divide-gray-200">
          <thead className="bg-gray-50 border-b border-gray-200">
            <tr>
              <th className="px-6 py-4 text-left text-xs font-bold text-sj-primary uppercase tracking-wider">Name</th>
              <th className="px-6 py-4 text-left text-xs font-bold text-sj-primary uppercase tracking-wider">Roll Number</th>
              <th className="px-6 py-4 text-left text-xs font-bold text-sj-primary uppercase tracking-wider">Department</th>
              <th className="px-6 py-4 text-left text-xs font-bold text-sj-primary uppercase tracking-wider">Registered</th>
              <th className="px-6 py-4 text-left text-xs font-bold text-sj-primary uppercase tracking-wider">Action</th>
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-gray-200">
              {loading ? <tr><td colSpan="5" className="p-4 text-center">Loading...</td></tr> : 
               students.map(student => (
                <tr key={student.id}>
                  <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900 flex items-center gap-3">
                    <div className="w-8 h-8 rounded-full bg-blue-50 text-sj-primary flex items-center justify-center font-bold text-sm border border-blue-100">
                      {student.name.charAt(0)}
                    </div>
                    {student.name}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{student.roll_number}</td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{student.department}</td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    {student.face_registered ? (
                      <span className="px-2 py-1 text-xs font-semibold bg-green-100 text-green-800 rounded-full">Yes</span>
                    ) : (
                      <span className="px-2 py-1 text-xs font-semibold bg-red-100 text-red-800 rounded-full">No</span>
                    )}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm">
                    <a href={`/students/${student.id}`} className="text-sj-primary hover:text-sj-primary/80 font-bold transition-colors">View</a>
                  </td>
                </tr>
              ))}
            </tbody>
        </table>
      </div>
    </div>
  );
};

export default Students;
