import React, { useState } from 'react';
import styled from 'styled-components';
import { useQuery } from 'react-query';
import { api } from '../services/api';
import { Users, Search, Filter, Star, Download, Eye, Mail, Phone, MapPin, Calendar, Award, Briefcase } from 'lucide-react';
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

const SearchContainer = styled.div`
  display: flex;
  gap: ${props => props.theme.spacing.md};
  margin-bottom: ${props => props.theme.spacing.lg};
`;

const SearchInput = styled.input`
  flex: 1;
  padding: ${props => props.theme.spacing.md};
  border: 1px solid ${props => props.theme.colors.border};
  border-radius: ${props => props.theme.borderRadius.md};
  font-size: 1rem;

  &:focus {
    outline: none;
    border-color: ${props => props.theme.colors.primary};
  }
`;

const FilterSelect = styled.select`
  padding: ${props => props.theme.spacing.md};
  border: 1px solid ${props => props.theme.colors.border};
  border-radius: ${props => props.theme.borderRadius.md};
  font-size: 1rem;
  background: white;
  cursor: pointer;
`;

const CandidateGrid = styled.div`
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
  gap: ${props => props.theme.spacing.lg};
`;

const CandidateCard = styled.div`
  background: ${props => props.theme.colors.surface};
  border: 1px solid ${props => props.theme.colors.border};
  border-radius: ${props => props.theme.borderRadius.lg};
  padding: ${props => props.theme.spacing.lg};
  box-shadow: ${props => props.theme.shadows.sm};
  transition: all 0.2s;

  &:hover {
    box-shadow: ${props => props.theme.shadows.md};
    transform: translateY(-2px);
  }
`;

const CandidateHeader = styled.div`
  display: flex;
  align-items: center;
  gap: ${props => props.theme.spacing.md};
  margin-bottom: ${props => props.theme.spacing.md};
`;

const CandidateIcon = styled.div`
  width: 50px;
  height: 50px;
  background: ${props => props.theme.colors.primary};
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-weight: bold;
  font-size: 1.2rem;
`;

const CandidateInfo = styled.div`
  flex: 1;
`;

const CandidateName = styled.h3`
  font-size: 1.2rem;
  font-weight: 600;
  color: ${props => props.theme.colors.text};
  margin-bottom: ${props => props.theme.spacing.xs};
`;

const CandidateRole = styled.p`
  color: ${props => props.theme.colors.textSecondary};
  font-size: 0.9rem;
`;

const CandidateDetails = styled.div`
  margin-bottom: ${props => props.theme.spacing.md};
`;

const DetailItem = styled.div`
  display: flex;
  align-items: center;
  gap: ${props => props.theme.spacing.sm};
  margin-bottom: ${props => props.theme.spacing.xs};
  font-size: 0.9rem;
  color: ${props => props.theme.colors.textSecondary};
`;

const SkillsContainer = styled.div`
  margin-bottom: ${props => props.theme.spacing.md};
`;

const SkillsTitle = styled.h4`
  font-size: 0.9rem;
  font-weight: 600;
  color: ${props => props.theme.colors.text};
  margin-bottom: ${props => props.theme.spacing.sm};
`;

const SkillsList = styled.div`
  display: flex;
  flex-wrap: wrap;
  gap: ${props => props.theme.spacing.xs};
`;

const SkillTag = styled.span`
  background: ${props => props.theme.colors.background};
  color: ${props => props.theme.colors.textSecondary};
  padding: ${props => props.theme.spacing.xs} ${props => props.theme.spacing.sm};
  border-radius: ${props => props.theme.borderRadius.sm};
  font-size: 0.8rem;
`;

const ActionsContainer = styled.div`
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

const MatchScore = styled.div`
  display: flex;
  align-items: center;
  gap: ${props => props.theme.spacing.xs};
  background: ${props => props.theme.colors.success};
  color: white;
  padding: ${props => props.theme.spacing.xs} ${props => props.theme.spacing.sm};
  border-radius: ${props => props.theme.borderRadius.sm};
  font-size: 0.8rem;
  font-weight: 500;
`;

const EmptyState = styled.div`
  text-align: center;
  padding: ${props => props.theme.spacing.xxl};
  color: ${props => props.theme.colors.textSecondary};
`;

function CandidatesList() {
  const [searchTerm, setSearchTerm] = useState('');
  const [filterBy, setFilterBy] = useState('all');

  const { data: resumes, isLoading, error } = useQuery(
    'all-candidates',
    () => api.get('/api/candidates').then(res => res.data),
    {
      onError: (error) => {
        toast.error('Failed to load candidates');
      }
    }
  );

  const { data: jobs } = useQuery(
    'jobs-for-matching',
    () => api.get('/api/jobs').then(res => res.data),
    {
      onError: (error) => {
        console.error('Failed to load jobs:', error);
      }
    }
  );

  // Filter candidates based on search and filter
  const filteredCandidates = resumes?.filter(candidate => {
    const matchesSearch = searchTerm === '' || 
      candidate.filename.toLowerCase().includes(searchTerm.toLowerCase()) ||
      candidate.content.toLowerCase().includes(searchTerm.toLowerCase());
    
    // Add more filtering logic here based on filterBy
    return matchesSearch;
  }) || [];

  const getInitials = (filename) => {
    return filename.charAt(0).toUpperCase();
  };

  const extractSkills = (content) => {
    // Simple skill extraction - in a real app, you'd use NLP
    const commonSkills = [
      'JavaScript', 'Python', 'React', 'Node.js', 'SQL', 'AWS', 'Docker',
      'Git', 'HTML', 'CSS', 'Java', 'C++', 'Machine Learning', 'Data Analysis',
      'Project Management', 'Agile', 'Scrum', 'Leadership', 'Communication'
    ];
    
    const foundSkills = commonSkills.filter(skill => 
      content.toLowerCase().includes(skill.toLowerCase())
    );
    
    return foundSkills.slice(0, 5); // Show top 5 skills
  };

  const getMatchScore = (candidate) => {
    // Simple match scoring - in a real app, you'd use more sophisticated matching
    return Math.floor(Math.random() * 40) + 60; // Random score between 60-100
  };

  if (isLoading) {
    return (
      <Container>
        <EmptyState>
          <Users size={48} />
          <p>Loading candidates...</p>
        </EmptyState>
      </Container>
    );
  }

  if (error) {
    return (
      <Container>
        <EmptyState>
          <Users size={48} />
          <p>Failed to load candidates</p>
        </EmptyState>
      </Container>
    );
  }

  return (
    <Container>
      <Header>
        <Title>All Candidates</Title>
        <MatchScore>
          <Star size={16} />
          {filteredCandidates.length} candidates found
        </MatchScore>
      </Header>

      <SearchContainer>
        <SearchInput
          type="text"
          placeholder="Search candidates by name, skills, or experience..."
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
        />
        <FilterSelect value={filterBy} onChange={(e) => setFilterBy(e.target.value)}>
          <option value="all">All Candidates</option>
          <option value="high-match">High Match (>80%)</option>
          <option value="recent">Recently Added</option>
          <option value="skills">By Skills</option>
        </FilterSelect>
      </SearchContainer>

      {filteredCandidates.length === 0 ? (
        <EmptyState>
          <Users size={48} />
          <p>No candidates found</p>
          <p>Try adjusting your search criteria</p>
        </EmptyState>
      ) : (
        <CandidateGrid>
          {filteredCandidates.map((candidate) => {
            const skills = extractSkills(candidate.content);
            const matchScore = getMatchScore(candidate);
            
            return (
              <CandidateCard key={candidate.id}>
                <CandidateHeader>
                  <CandidateIcon>
                    {getInitials(candidate.filename)}
                  </CandidateIcon>
                  <CandidateInfo>
                    <CandidateName>{candidate.filename.replace('.pdf', '').replace('.docx', '').replace('.doc', '').replace('.txt', '')}</CandidateName>
                    <CandidateRole>Software Developer</CandidateRole>
                  </CandidateInfo>
                  <MatchScore>
                    <Star size={14} />
                    {matchScore}%
                  </MatchScore>
                </CandidateHeader>

                <CandidateDetails>
                  <DetailItem>
                    <Calendar size={16} />
                    Added {new Date(candidate.created_at).toLocaleDateString()}
                  </DetailItem>
                  <DetailItem>
                    <Briefcase size={16} />
                    3+ years experience
                  </DetailItem>
                  <DetailItem>
                    <Award size={16} />
                    Bachelor's Degree
                  </DetailItem>
                </CandidateDetails>

                <SkillsContainer>
                  <SkillsTitle>Key Skills:</SkillsTitle>
                  <SkillsList>
                    {skills.map((skill, index) => (
                      <SkillTag key={index}>{skill}</SkillTag>
                    ))}
                    {skills.length === 0 && (
                      <SkillTag>Skills not detected</SkillTag>
                    )}
                  </SkillsList>
                </SkillsContainer>

                <ActionsContainer>
                  <ActionButton
                    onClick={() => window.open(`/candidates/${candidate.id}`, '_blank')}
                  >
                    <Eye size={16} />
                    View Details
                  </ActionButton>
                  <ActionButton variant="primary">
                    <Download size={16} />
                    Download
                  </ActionButton>
                </ActionsContainer>
              </CandidateCard>
            );
          })}
        </CandidateGrid>
      )}
    </Container>
  );
}

export default CandidatesList;
