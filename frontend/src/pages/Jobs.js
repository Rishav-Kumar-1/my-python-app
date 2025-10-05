import React, { useState } from 'react';
import styled from 'styled-components';
import { useQuery, useMutation, useQueryClient } from 'react-query';
import { api } from '../services/api';
import { Briefcase, Plus, Search, Users, FileText } from 'lucide-react';
import toast from 'react-hot-toast';

const Container = styled.div`
  max-width: 1200px;
  margin: 0 auto;
`;

const Header = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: ${props => props.theme.spacing.xl};
`;

const Title = styled.h1`
  font-size: 2rem;
  font-weight: bold;
  color: ${props => props.theme.colors.text};
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
  display: flex;
  align-items: center;
  gap: ${props => props.theme.spacing.sm};
  transition: background-color 0.2s;

  &:hover {
    background: #2563eb;
  }
`;

const Modal = styled.div`
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
`;

const ModalContent = styled.div`
  background: ${props => props.theme.colors.surface};
  border-radius: ${props => props.theme.borderRadius.lg};
  padding: ${props => props.theme.spacing.xl};
  width: 90%;
  max-width: 600px;
  max-height: 80vh;
  overflow-y: auto;
`;

const ModalHeader = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: ${props => props.theme.spacing.lg};
`;

const ModalTitle = styled.h2`
  font-size: 1.5rem;
  font-weight: bold;
  color: ${props => props.theme.colors.text};
`;

const CloseButton = styled.button`
  background: none;
  border: none;
  font-size: 1.5rem;
  cursor: pointer;
  color: ${props => props.theme.colors.textSecondary};
`;

const Form = styled.form`
  display: flex;
  flex-direction: column;
  gap: ${props => props.theme.spacing.lg};
`;

const Input = styled.input`
  padding: ${props => props.theme.spacing.md};
  border: 1px solid ${props => props.theme.colors.border};
  border-radius: ${props => props.theme.borderRadius.md};
  font-size: 1rem;

  &:focus {
    outline: none;
    border-color: ${props => props.theme.colors.primary};
  }
`;

const TextArea = styled.textarea`
  padding: ${props => props.theme.spacing.md};
  border: 1px solid ${props => props.theme.colors.border};
  border-radius: ${props => props.theme.borderRadius.md};
  font-size: 1rem;
  min-height: 120px;
  resize: vertical;

  &:focus {
    outline: none;
    border-color: ${props => props.theme.colors.primary};
  }
`;

const JobGrid = styled.div`
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: ${props => props.theme.spacing.lg};
`;

const JobCard = styled.div`
  background: ${props => props.theme.colors.surface};
  border: 1px solid ${props => props.theme.colors.border};
  border-radius: ${props => props.theme.borderRadius.lg};
  padding: ${props => props.theme.spacing.lg};
  box-shadow: ${props => props.theme.shadows.sm};
  transition: box-shadow 0.2s;

  &:hover {
    box-shadow: ${props => props.theme.shadows.md};
  }
`;

const JobHeader = styled.div`
  display: flex;
  align-items: center;
  gap: ${props => props.theme.spacing.md};
  margin-bottom: ${props => props.theme.spacing.md};
`;

const JobIcon = styled.div`
  color: ${props => props.theme.colors.primary};
`;

const JobTitle = styled.h3`
  font-size: 1.2rem;
  font-weight: 600;
  color: ${props => props.theme.colors.text};
  margin-bottom: ${props => props.theme.spacing.sm};
`;

const JobDescription = styled.p`
  color: ${props => props.theme.colors.textSecondary};
  line-height: 1.5;
  margin-bottom: ${props => props.theme.spacing.md};
`;

const JobActions = styled.div`
  display: flex;
  gap: ${props => props.theme.spacing.sm};
`;

const ActionButton = styled.button`
  background: ${props => props.variant === 'primary' ? props.theme.colors.primary : 'transparent'};
  color: ${props => props.variant === 'primary' ? 'white' : props.theme.colors.primary};
  border: 1px solid ${props => props.theme.colors.primary};
  padding: ${props => props.theme.spacing.sm} ${props => props.theme.spacing.md};
  border-radius: ${props => props.theme.borderRadius.md};
  font-size: 0.9rem;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: ${props => props.theme.spacing.xs};
  transition: all 0.2s;

  &:hover {
    background: ${props => props.variant === 'primary' ? '#2563eb' : props.theme.colors.primary};
    color: white;
  }
`;

const MatchModal = styled(Modal)``;

const MatchContent = styled.div`
  background: ${props => props.theme.colors.surface};
  border-radius: ${props => props.theme.borderRadius.lg};
  padding: ${props => props.theme.spacing.xl};
  width: 90%;
  max-width: 800px;
  max-height: 80vh;
  overflow-y: auto;
`;

const CandidateList = styled.div`
  display: flex;
  flex-direction: column;
  gap: ${props => props.theme.spacing.md};
`;

const CandidateCard = styled.div`
  background: ${props => props.theme.colors.background};
  border: 1px solid ${props => props.theme.colors.border};
  border-radius: ${props => props.theme.borderRadius.md};
  padding: ${props => props.theme.spacing.lg};
`;

const CandidateHeader = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: ${props => props.theme.spacing.md};
`;

const CandidateName = styled.h4`
  font-weight: 600;
  color: ${props => props.theme.colors.text};
`;

const MatchScore = styled.span`
  background: ${props => props.theme.colors.primary};
  color: white;
  padding: ${props => props.theme.spacing.xs} ${props => props.theme.spacing.sm};
  border-radius: ${props => props.theme.borderRadius.sm};
  font-size: 0.8rem;
  font-weight: 500;
`;

const EvidenceList = styled.ul`
  list-style: none;
  margin: ${props => props.theme.spacing.md} 0;
`;

const EvidenceItem = styled.li`
  background: ${props => props.theme.colors.surface};
  padding: ${props => props.theme.spacing.sm};
  border-radius: ${props => props.theme.borderRadius.sm};
  margin-bottom: ${props => props.theme.spacing.sm};
  font-size: 0.9rem;
  color: ${props => props.theme.colors.textSecondary};
`;

const MissingRequirements = styled.div`
  margin-top: ${props => props.theme.spacing.md};
`;

const MissingTitle = styled.h5`
  font-weight: 600;
  color: ${props => props.theme.colors.error};
  margin-bottom: ${props => props.theme.spacing.sm};
`;

const MissingList = styled.ul`
  list-style: none;
`;

const MissingItem = styled.li`
  color: ${props => props.theme.colors.textSecondary};
  font-size: 0.9rem;
  margin-bottom: ${props => props.theme.spacing.xs};
`;

function Jobs() {
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [showMatchModal, setShowMatchModal] = useState(false);
  const [selectedJob, setSelectedJob] = useState(null);
  const [matchResults, setMatchResults] = useState(null);
  const [formData, setFormData] = useState({
    title: '',
    description: '',
    requirements: ''
  });

  const queryClient = useQueryClient();

  const { data: jobs, isLoading } = useQuery(
    'jobs',
    () => api.get('/api/jobs').then(res => res.data),
    {
      onError: (error) => {
        toast.error('Failed to load jobs');
      }
    }
  );

  const createJobMutation = useMutation(
    async (jobData) => {
      const response = await api.post('/api/jobs', jobData);
      return response.data;
    },
    {
      onSuccess: () => {
        toast.success('Job created successfully!');
        queryClient.invalidateQueries('jobs');
        setShowCreateModal(false);
        setFormData({ title: '', description: '', requirements: '' });
      },
      onError: (error) => {
        toast.error(error.response?.data?.error?.message || 'Failed to create job');
      }
    }
  );

  const matchMutation = useMutation(
    async (jobId) => {
      const response = await api.post(`/api/jobs/${jobId}/match`, { top_n: 10 });
      return response.data;
    },
    {
      onSuccess: (data) => {
        setMatchResults(data);
        setShowMatchModal(true);
      },
      onError: (error) => {
        toast.error('Failed to match candidates');
      }
    }
  );

  const handleCreateJob = (e) => {
    e.preventDefault();
    createJobMutation.mutate(formData);
  };

  const handleMatch = (job) => {
    setSelectedJob(job);
    matchMutation.mutate(job.id);
  };

  const handleInputChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    });
  };

  return (
    <Container>
      <Header>
        <Title>Job Postings</Title>
        <Button onClick={() => setShowCreateModal(true)}>
          <Plus size={20} />
          Create Job
        </Button>
      </Header>

      {isLoading ? (
        <div>Loading jobs...</div>
      ) : jobs && jobs.length > 0 ? (
        <JobGrid>
          {jobs.map((job) => (
            <JobCard key={job.id}>
              <JobHeader>
                <JobIcon>
                  <Briefcase size={24} />
                </JobIcon>
                <div>
                  <JobTitle>{job.title}</JobTitle>
                </div>
              </JobHeader>
              <JobDescription>
                {job.description.length > 150 
                  ? `${job.description.substring(0, 150)}...` 
                  : job.description
                }
              </JobDescription>
              <JobActions>
                <ActionButton onClick={() => handleMatch(job)}>
                  <Users size={16} />
                  Match Candidates
                </ActionButton>
              </JobActions>
            </JobCard>
          ))}
        </JobGrid>
      ) : (
        <div style={{ textAlign: 'center', padding: '2rem', color: '#64748b' }}>
          <Briefcase size={48} style={{ marginBottom: '1rem' }} />
          <p>No jobs created yet. Create your first job posting!</p>
        </div>
      )}

      {showCreateModal && (
        <Modal>
          <ModalContent>
            <ModalHeader>
              <ModalTitle>Create Job Posting</ModalTitle>
              <CloseButton onClick={() => setShowCreateModal(false)}>×</CloseButton>
            </ModalHeader>
            <Form onSubmit={handleCreateJob}>
              <Input
                type="text"
                name="title"
                placeholder="Job Title"
                value={formData.title}
                onChange={handleInputChange}
                required
              />
              <TextArea
                name="description"
                placeholder="Job Description"
                value={formData.description}
                onChange={handleInputChange}
                required
              />
              <TextArea
                name="requirements"
                placeholder="Requirements"
                value={formData.requirements}
                onChange={handleInputChange}
                required
              />
              <Button type="submit" disabled={createJobMutation.isLoading}>
                {createJobMutation.isLoading ? 'Creating...' : 'Create Job'}
              </Button>
            </Form>
          </ModalContent>
        </Modal>
      )}

      {showMatchModal && matchResults && (
        <MatchModal>
          <MatchContent>
            <ModalHeader>
              <ModalTitle>Candidate Matches for {selectedJob?.title}</ModalTitle>
              <CloseButton onClick={() => setShowMatchModal(false)}>×</CloseButton>
            </ModalHeader>
            <CandidateList>
              {matchResults.candidates.map((candidate, index) => (
                <CandidateCard key={index}>
                  <CandidateHeader>
                    <CandidateName>{candidate.filename}</CandidateName>
                    <MatchScore>
                      {(candidate.match_score * 100).toFixed(1)}% Match
                    </MatchScore>
                  </CandidateHeader>
                  
                  {candidate.evidence && candidate.evidence.length > 0 && (
                    <div>
                      <h5 style={{ fontWeight: '600', marginBottom: '0.5rem' }}>Evidence:</h5>
                      <EvidenceList>
                        {candidate.evidence.map((evidence, idx) => (
                          <EvidenceItem key={idx}>{evidence}</EvidenceItem>
                        ))}
                      </EvidenceList>
                    </div>
                  )}
                  
                  {candidate.missing_requirements && candidate.missing_requirements.length > 0 && (
                    <MissingRequirements>
                      <MissingTitle>Missing Requirements:</MissingTitle>
                      <MissingList>
                        {candidate.missing_requirements.map((req, idx) => (
                          <MissingItem key={idx}>• {req}</MissingItem>
                        ))}
                      </MissingList>
                    </MissingRequirements>
                  )}
                </CandidateCard>
              ))}
            </CandidateList>
          </MatchContent>
        </MatchModal>
      )}
    </Container>
  );
}

export default Jobs;
