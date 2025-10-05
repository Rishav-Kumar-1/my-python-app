import React, { useState } from 'react';
import styled from 'styled-components';
import { useQuery } from 'react-query';
import { api } from '../services/api';
import { Search as SearchIcon, File, MessageSquare } from 'lucide-react';
import toast from 'react-hot-toast';

const Container = styled.div`
  max-width: 1000px;
  margin: 0 auto;
`;

const Title = styled.h1`
  font-size: 2rem;
  font-weight: bold;
  color: ${props => props.theme.colors.text};
  margin-bottom: ${props => props.theme.spacing.lg};
`;

const SearchContainer = styled.div`
  background: ${props => props.theme.colors.surface};
  border-radius: ${props => props.theme.borderRadius.lg};
  padding: ${props => props.theme.spacing.xl};
  box-shadow: ${props => props.theme.shadows.md};
  margin-bottom: ${props => props.theme.spacing.xl};
`;

const SearchForm = styled.form`
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

const SearchButton = styled.button`
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

  &:disabled {
    background: ${props => props.theme.colors.textSecondary};
    cursor: not-allowed;
  }
`;

const ResultsContainer = styled.div`
  display: flex;
  flex-direction: column;
  gap: ${props => props.theme.spacing.lg};
`;

const ResultCard = styled.div`
  background: ${props => props.theme.colors.surface};
  border: 1px solid ${props => props.theme.colors.border};
  border-radius: ${props => props.theme.borderRadius.lg};
  padding: ${props => props.theme.spacing.lg};
  box-shadow: ${props => props.theme.shadows.sm};
`;

const ResultHeader = styled.div`
  display: flex;
  align-items: center;
  gap: ${props => props.theme.spacing.md};
  margin-bottom: ${props => props.theme.spacing.md};
`;

const ResultIcon = styled.div`
  color: ${props => props.theme.colors.primary};
`;

const ResultInfo = styled.div`
  flex: 1;
`;

const ResultTitle = styled.h3`
  font-size: 1.1rem;
  font-weight: 600;
  color: ${props => props.theme.colors.text};
  margin-bottom: ${props => props.theme.spacing.xs};
`;

const ResultScore = styled.span`
  background: ${props => props.theme.colors.primary};
  color: white;
  padding: ${props => props.theme.spacing.xs} ${props => props.theme.spacing.sm};
  border-radius: ${props => props.theme.borderRadius.sm};
  font-size: 0.8rem;
  font-weight: 500;
`;

const ResultSnippet = styled.p`
  color: ${props => props.theme.colors.textSecondary};
  line-height: 1.6;
  background: ${props => props.theme.colors.background};
  padding: ${props => props.theme.spacing.md};
  border-radius: ${props => props.theme.borderRadius.md};
  border-left: 4px solid ${props => props.theme.colors.primary};
`;

const NoResults = styled.div`
  text-align: center;
  padding: ${props => props.theme.spacing.xxl};
  color: ${props => props.theme.colors.textSecondary};
`;

const LoadingSpinner = styled.div`
  display: flex;
  justify-content: center;
  align-items: center;
  padding: ${props => props.theme.spacing.xxl};
`;

function Search() {
  const [query, setQuery] = useState('');
  const [searchQuery, setSearchQuery] = useState('');

  const { data: searchResults, isLoading, error } = useQuery(
    ['search', searchQuery],
    () => api.post('/api/ask', { query: searchQuery, k: 10 }).then(res => res.data),
    {
      enabled: !!searchQuery,
      onError: (error) => {
        toast.error('Search failed');
      }
    }
  );

  const handleSubmit = (e) => {
    e.preventDefault();
    if (query.trim()) {
      setSearchQuery(query.trim());
    }
  };

  return (
    <Container>
      <Title>Search Resumes</Title>
      
      <SearchContainer>
        <SearchForm onSubmit={handleSubmit}>
          <SearchInput
            type="text"
            placeholder="Ask a question about your resumes..."
            value={query}
            onChange={(e) => setQuery(e.target.value)}
          />
          <SearchButton type="submit" disabled={!query.trim()}>
            <SearchIcon size={20} />
            Search
          </SearchButton>
        </SearchForm>
      </SearchContainer>

      {isLoading && (
        <LoadingSpinner>
          <div>Searching...</div>
        </LoadingSpinner>
      )}

      {error && (
        <NoResults>
          <MessageSquare size={48} />
          <p>Error occurred during search</p>
        </NoResults>
      )}

      {searchResults && !isLoading && (
        <ResultsContainer>
          <h2>Search Results</h2>
          {searchResults.evidence && searchResults.evidence.length > 0 ? (
            searchResults.evidence.map((result, index) => (
              <ResultCard key={index}>
                <ResultHeader>
                  <ResultIcon>
                    <File size={20} />
                  </ResultIcon>
                  <ResultInfo>
                    <ResultTitle>{result.filename}</ResultTitle>
                    <ResultScore>Score: {(result.score * 100).toFixed(1)}%</ResultScore>
                  </ResultInfo>
                </ResultHeader>
                <ResultSnippet>{result.snippet}</ResultSnippet>
              </ResultCard>
            ))
          ) : (
            <NoResults>
              <MessageSquare size={48} />
              <p>No results found for your query</p>
            </NoResults>
          )}
        </ResultsContainer>
      )}

      {!searchQuery && !isLoading && (
        <NoResults>
          <SearchIcon size={48} />
          <p>Enter a search query to find relevant information in your resumes</p>
        </NoResults>
      )}
    </Container>
  );
}

export default Search;
