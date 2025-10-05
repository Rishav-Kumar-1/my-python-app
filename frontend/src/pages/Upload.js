import React, { useState } from 'react';
import { useDropzone } from 'react-dropzone';
import styled from 'styled-components';
import { useQuery, useMutation, useQueryClient } from 'react-query';
import { api } from '../services/api';
import { Upload as UploadIcon, File, X, CheckCircle, AlertCircle } from 'lucide-react';
import toast from 'react-hot-toast';

const Container = styled.div`
  max-width: 800px;
  margin: 0 auto;
`;

const Title = styled.h1`
  font-size: 2rem;
  font-weight: bold;
  color: ${props => props.theme.colors.text};
  margin-bottom: ${props => props.theme.spacing.lg};
`;

const UploadArea = styled.div`
  border: 2px dashed ${props => props.isDragActive ? props.theme.colors.primary : props.theme.colors.border};
  border-radius: ${props => props.theme.borderRadius.lg};
  padding: ${props => props.theme.spacing.xxl};
  text-align: center;
  background: ${props => props.isDragActive ? props.theme.colors.background : 'transparent'};
  transition: all 0.2s;
  cursor: pointer;
  margin-bottom: ${props => props.theme.spacing.lg};

  &:hover {
    border-color: ${props => props.theme.colors.primary};
    background: ${props => props.theme.colors.background};
  }
`;

const UploadIconWrapper = styled.div`
  color: ${props => props.theme.colors.textSecondary};
  margin-bottom: ${props => props.theme.spacing.md};
`;

const UploadText = styled.p`
  font-size: 1.1rem;
  color: ${props => props.theme.colors.text};
  margin-bottom: ${props => props.theme.spacing.sm};
`;

const UploadSubtext = styled.p`
  color: ${props => props.theme.colors.textSecondary};
  font-size: 0.9rem;
`;

const FileList = styled.div`
  display: flex;
  flex-direction: column;
  gap: ${props => props.theme.spacing.md};
`;

const FileItem = styled.div`
  display: flex;
  align-items: center;
  gap: ${props => props.theme.spacing.md};
  padding: ${props => props.theme.spacing.md};
  background: ${props => props.theme.colors.surface};
  border: 1px solid ${props => props.theme.colors.border};
  border-radius: ${props => props.theme.borderRadius.md};
`;

const FileIcon = styled.div`
  color: ${props => props.theme.colors.textSecondary};
`;

const FileInfo = styled.div`
  flex: 1;
`;

const FileName = styled.p`
  font-weight: 500;
  color: ${props => props.theme.colors.text};
`;

const FileSize = styled.p`
  font-size: 0.9rem;
  color: ${props => props.theme.colors.textSecondary};
`;

const StatusIcon = styled.div`
  color: ${props => {
    if (props.status === 'success') return props.theme.colors.success;
    if (props.status === 'error') return props.theme.colors.error;
    return props.theme.colors.textSecondary;
  }};
`;

const RemoveButton = styled.button`
  background: none;
  border: none;
  color: ${props => props.theme.colors.textSecondary};
  cursor: pointer;
  padding: ${props => props.theme.spacing.sm};

  &:hover {
    color: ${props => props.theme.colors.error};
  }
`;

const Button = styled.button`
  background: ${props => props.theme.colors.primary};
  color: white;
  border: none;
  padding: ${props => props.theme.spacing.md} ${props => props.theme.spacing.lg};
  border-radius: ${props => props.theme.borderRadius.md};
  font-size: 1rem;
  font-weight: 500;
  cursor: pointer;
  transition: background-color 0.2s;
  margin-top: ${props => props.theme.spacing.lg};

  &:hover {
    background: #2563eb;
  }

  &:disabled {
    background: ${props => props.theme.colors.textSecondary};
    cursor: not-allowed;
  }
`;

const ResumeList = styled.div`
  margin-top: ${props => props.theme.spacing.xxl};
`;

const ResumeItem = styled.div`
  display: flex;
  align-items: center;
  gap: ${props => props.theme.spacing.md};
  padding: ${props => props.theme.spacing.md};
  background: ${props => props.theme.colors.surface};
  border: 1px solid ${props => props.theme.colors.border};
  border-radius: ${props => props.theme.borderRadius.md};
  margin-bottom: ${props => props.theme.spacing.md};
`;

const ResumeInfo = styled.div`
  flex: 1;
`;

const ResumeName = styled.p`
  font-weight: 500;
  color: ${props => props.theme.colors.text};
`;

const ResumeDate = styled.p`
  font-size: 0.9rem;
  color: ${props => props.theme.colors.textSecondary};
`;

function Upload() {
  const [files, setFiles] = useState([]);
  const [uploading, setUploading] = useState(false);
  const queryClient = useQueryClient();

  const { data: resumes, isLoading } = useQuery(
    'resumes',
    () => api.get('/api/resumes').then(res => res.data.items),
    {
      onError: (error) => {
        toast.error('Failed to load resumes');
      }
    }
  );

  const uploadMutation = useMutation(
    async (formData) => {
      const response = await api.post('/api/resumes', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });
      return response.data;
    },
    {
      onSuccess: () => {
        toast.success('Resume uploaded successfully!');
        queryClient.invalidateQueries('resumes');
        setFiles([]);
      },
      onError: (error) => {
        toast.error(error.response?.data?.error?.message || 'Upload failed');
      }
    }
  );

  const bulkUploadMutation = useMutation(
    async (formData) => {
      const response = await api.post('/api/resumes/bulk', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });
      return response.data;
    },
    {
      onSuccess: (data) => {
        toast.success(`${data.length} resumes uploaded successfully!`);
        queryClient.invalidateQueries('resumes');
        setFiles([]);
      },
      onError: (error) => {
        toast.error(error.response?.data?.error?.message || 'Bulk upload failed');
      }
    }
  );

  const onDrop = (acceptedFiles) => {
    const newFiles = acceptedFiles.map(file => ({
      file,
      id: Math.random().toString(36).substr(2, 9),
      status: 'pending'
    }));
    setFiles(prev => [...prev, ...newFiles]);
  };

  const removeFile = (fileId) => {
    setFiles(prev => prev.filter(f => f.id !== fileId));
  };

  const handleUpload = async () => {
    if (files.length === 0) return;

    setUploading(true);

    try {
      if (files.length === 1 && files[0].file.name.endsWith('.zip')) {
        // Bulk upload
        const formData = new FormData();
        formData.append('file', files[0].file);
        await bulkUploadMutation.mutateAsync(formData);
      } else {
        // Individual uploads
        for (const fileItem of files) {
          const formData = new FormData();
          formData.append('file', fileItem.file);
          await uploadMutation.mutateAsync(formData);
        }
      }
    } catch (error) {
      console.error('Upload error:', error);
    } finally {
      setUploading(false);
    }
  };

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'application/pdf': ['.pdf'],
      'application/vnd.openxmlformats-officedocument.wordprocessingml.document': ['.docx'],
      'application/msword': ['.doc'],
      'text/plain': ['.txt'],
      'application/zip': ['.zip']
    },
    multiple: true
  });

  const formatFileSize = (bytes) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString();
  };

  return (
    <Container>
      <Title>Upload Resumes</Title>
      
      <UploadArea {...getRootProps()} isDragActive={isDragActive}>
        <input {...getInputProps()} />
        <UploadIconWrapper>
          <UploadIcon size={48} />
        </UploadIconWrapper>
        <UploadText>
          {isDragActive ? 'Drop the files here...' : 'Drag & drop resumes here, or click to select'}
        </UploadText>
        <UploadSubtext>
          Supports PDF, DOCX, DOC, TXT files. ZIP files for bulk upload.
        </UploadSubtext>
      </UploadArea>

      {files.length > 0 && (
        <>
          <FileList>
            {files.map((fileItem) => (
              <FileItem key={fileItem.id}>
                <FileIcon>
                  <File size={20} />
                </FileIcon>
                <FileInfo>
                  <FileName>{fileItem.file.name}</FileName>
                  <FileSize>{formatFileSize(fileItem.file.size)}</FileSize>
                </FileInfo>
                <StatusIcon status={fileItem.status}>
                  {fileItem.status === 'success' && <CheckCircle size={20} />}
                  {fileItem.status === 'error' && <AlertCircle size={20} />}
                </StatusIcon>
                <RemoveButton onClick={() => removeFile(fileItem.id)}>
                  <X size={20} />
                </RemoveButton>
              </FileItem>
            ))}
          </FileList>

          <Button 
            onClick={handleUpload} 
            disabled={uploading || uploadMutation.isLoading || bulkUploadMutation.isLoading}
          >
            {uploading ? 'Uploading...' : `Upload ${files.length} file${files.length > 1 ? 's' : ''}`}
          </Button>
        </>
      )}

      <ResumeList>
        <Title>Your Resumes</Title>
        {isLoading ? (
          <p>Loading resumes...</p>
        ) : resumes && resumes.length > 0 ? (
          resumes.map((resume) => (
            <ResumeItem key={resume.id}>
              <FileIcon>
                <File size={20} />
              </FileIcon>
              <ResumeInfo>
                <ResumeName>{resume.filename}</ResumeName>
                <ResumeDate>Uploaded {formatDate(resume.created_at)}</ResumeDate>
              </ResumeInfo>
            </ResumeItem>
          ))
        ) : (
          <p>No resumes uploaded yet.</p>
        )}
      </ResumeList>
    </Container>
  );
}

export default Upload;
