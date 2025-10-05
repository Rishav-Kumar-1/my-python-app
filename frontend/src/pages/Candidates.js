import React from 'react';
import { useParams } from 'react-router-dom';
import styled from 'styled-components';
import { useQuery } from 'react-query';
import { api } from '../services/api';
import { File, User, Calendar, Mail, Phone, MapPin } from 'lucide-react';

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

const CandidateCard = styled.div`
  background: ${props => props.theme.colors.surface};
  border: 1px solid ${props => props.theme.colors.border};
  border-radius: ${props => props.theme.borderRadius.lg};
  padding: ${props => props.theme.spacing.xl};
  box-shadow: ${props => props.theme.shadows.md};
`;

const CandidateHeader = styled.div`
  display: flex;
  align-items: center;
  gap: ${props => props.theme.spacing.lg};
  margin-bottom: ${props => props.theme.spacing.lg};
`;

const CandidateIcon = styled.div`
  color: ${props => props.theme.colors.primary};
`;

const CandidateInfo = styled.div`
  flex: 1;
`;

const CandidateName = styled.h2`
  font-size: 1.5rem;
  font-weight: 600;
  color: ${props => props.theme.colors.text};
  margin-bottom: ${props => props.theme.spacing.sm};
`;

const CandidateMeta = styled.div`
  display: flex;
  gap: ${props => props.theme.spacing.lg};
  color: ${props => props.theme.colors.textSecondary};
  font-size: 0.9rem;
`;

const MetaItem = styled.div`
  display: flex;
  align-items: center;
  gap: ${props => props.theme.spacing.xs};
`;

const ContentSection = styled.div`
  margin-bottom: ${props => props.theme.spacing.lg};
`;

const SectionTitle = styled.h3`
  font-size: 1.2rem;
  font-weight: 600;
  color: ${props => props.theme.colors.text};
  margin-bottom: ${props => props.theme.spacing.md};
  display: flex;
  align-items: center;
  gap: ${props => props.theme.spacing.sm};
`;

const SectionContent = styled.div`
  background: ${props => props.theme.colors.background};
  border: 1px solid ${props => props.theme.colors.border};
  border-radius: ${props => props.theme.borderRadius.md};
  padding: ${props => props.theme.spacing.lg};
  line-height: 1.6;
  color: ${props => props.theme.colors.text};
`;

const LoadingSpinner = styled.div`
  display: flex;
  justify-content: center;
  align-items: center;
  padding: ${props => props.theme.spacing.xxl};
`;

const ErrorMessage = styled.div`
  text-align: center;
  padding: ${props => props.theme.spacing.xxl};
  color: ${props => props.theme.colors.error};
`;

function Candidates() {
  const { id } = useParams();

  const { data: resume, isLoading, error } = useQuery(
    ['candidate', id],
    () => api.get(`/api/candidates/${id}`).then(res => res.data),
    {
      enabled: !!id,
      onError: (error) => {
        console.error('Failed to load candidate:', error);
      }
    }
  );

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'long',
      day: 'numeric'
    });
  };

  if (isLoading) {
    return (
      <Container>
        <LoadingSpinner>
          <div>Loading candidate details...</div>
        </LoadingSpinner>
      </Container>
    );
  }

  if (error) {
    return (
      <Container>
        <ErrorMessage>
          <File size={48} />
          <p>Failed to load candidate details</p>
        </ErrorMessage>
      </Container>
    );
  }

  if (!resume) {
    return (
      <Container>
        <ErrorMessage>
          <File size={48} />
          <p>Candidate not found</p>
        </ErrorMessage>
      </Container>
    );
  }

  return (
    <Container>
      <Title>Candidate Details</Title>
      
      <CandidateCard>
        <CandidateHeader>
          <CandidateIcon>
            <File size={32} />
          </CandidateIcon>
          <CandidateInfo>
            <CandidateName>{resume.filename}</CandidateName>
            <CandidateMeta>
              <MetaItem>
                <Calendar size={16} />
                Uploaded {formatDate(resume.created_at)}
              </MetaItem>
            </CandidateMeta>
          </CandidateInfo>
        </CandidateHeader>

        <ContentSection>
          <SectionTitle>
            <User size={20} />
            Resume Content
          </SectionTitle>
          <SectionContent>
            {resume.content}
          </SectionContent>
        </ContentSection>
      </CandidateCard>
    </Container>
  );
}

export default Candidates;
