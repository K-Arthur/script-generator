import React, { useState, useEffect } from 'react';
import {
  Box,
  Button,
  Container,
  FormControl,
  InputLabel,
  MenuItem,
  Select,
  TextField,
  Typography,
  Paper,
  CircularProgress,
  Alert,
} from '@mui/material';

const ScriptEditor = () => {
  const [content, setContent] = useState('');
  const [template, setTemplate] = useState('documentary');
  const [templates, setTemplates] = useState({});
  const [loading, setLoading] = useState(false);
  const [script, setScript] = useState('');
  const [error, setError] = useState(null);
  const [validation, setValidation] = useState(null);
  const [exportFormat, setExportFormat] = useState('txt');

  useEffect(() => {
    // Fetch available templates
    fetch('/api/templates')
      .then(response => response.json())
      .then(data => {
        if (data.status === 'success') {
          setTemplates(data.templates);
        }
      })
      .catch(err => setError('Failed to load templates'));
  }, []);

  const handleContentChange = (event) => {
    setContent(event.target.value);
  };

  const handleTemplateChange = (event) => {
    setTemplate(event.target.value);
  };

  const handleExportFormatChange = (event) => {
    setExportFormat(event.target.value);
  };

  const generateScript = async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await fetch('/api/generate-script', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          content,
          template_name: template,
        }),
      });
      const data = await response.json();
      if (data.status === 'success') {
        setScript(data.script);
        validateScript(data.script);
      } else {
        setError(data.detail || 'Failed to generate script');
      }
    } catch (err) {
      setError('Error generating script');
    } finally {
      setLoading(false);
    }
  };

  const validateScript = async (scriptContent) => {
    try {
      const response = await fetch('/api/validate-script', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          script: scriptContent,
          template_name: template,
        }),
      });
      const data = await response.json();
      if (data.status === 'success') {
        setValidation(data.validation);
      }
    } catch (err) {
      console.error('Error validating script:', err);
    }
  };

  const exportScript = async () => {
    try {
      const response = await fetch('/api/export-script', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          script,
          format: exportFormat,
        }),
      });
      
      if (response.ok) {
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `script.${exportFormat}`;
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
        document.body.removeChild(a);
      } else {
        setError('Failed to export script');
      }
    } catch (err) {
      setError('Error exporting script');
    }
  };

  return (
    <Container maxWidth="lg">
      <Box sx={{ my: 4 }}>
        <Typography variant="h4" component="h1" gutterBottom>
          AI Script Generator
        </Typography>

        {error && (
          <Alert severity="error" sx={{ mb: 2 }}>
            {error}
          </Alert>
        )}

        <Paper sx={{ p: 3, mb: 3 }}>
          <FormControl fullWidth sx={{ mb: 3 }}>
            <InputLabel>Template</InputLabel>
            <Select value={template} onChange={handleTemplateChange}>
              {Object.entries(templates).map(([key, value]) => (
                <MenuItem key={key} value={key}>
                  {value.name || key}
                </MenuItem>
              ))}
            </Select>
          </FormControl>

          <TextField
            fullWidth
            multiline
            rows={6}
            label="Content"
            value={content}
            onChange={handleContentChange}
            sx={{ mb: 3 }}
          />

          <Button
            variant="contained"
            onClick={generateScript}
            disabled={loading || !content}
            sx={{ mr: 2 }}
          >
            {loading ? <CircularProgress size={24} /> : 'Generate Script'}
          </Button>
        </Paper>

        {script && (
          <Paper sx={{ p: 3, mb: 3 }}>
            <Typography variant="h6" gutterBottom>
              Generated Script
            </Typography>
            
            <TextField
              fullWidth
              multiline
              rows={10}
              value={script}
              sx={{ mb: 3 }}
            />

            <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
              <FormControl sx={{ minWidth: 120 }}>
                <InputLabel>Export Format</InputLabel>
                <Select value={exportFormat} onChange={handleExportFormatChange}>
                  <MenuItem value="txt">Text</MenuItem>
                  <MenuItem value="html">HTML</MenuItem>
                  <MenuItem value="md">Markdown</MenuItem>
                </Select>
              </FormControl>

              <Button variant="contained" onClick={exportScript}>
                Export Script
              </Button>
            </Box>
          </Paper>
        )}

        {validation && (
          <Paper sx={{ p: 3 }}>
            <Typography variant="h6" gutterBottom>
              Script Analysis
            </Typography>
            
            <Typography variant="subtitle1">Readability</Typography>
            <Typography>
              Flesch Score: {validation.readability.flesch_score.toFixed(1)}
              <br />
              Grade Level: {validation.readability.grade_level.toFixed(1)}
              <br />
              Reading Time: {validation.readability.reading_time.toFixed(1)} minutes
            </Typography>

            <Typography variant="subtitle1" sx={{ mt: 2 }}>
              Structure
            </Typography>
            <Typography>
              Words: {validation.structure.word_count}
              <br />
              Sentences: {validation.structure.sentence_count}
              <br />
              Paragraphs: {validation.structure.paragraph_count}
            </Typography>

            <Typography variant="subtitle1" sx={{ mt: 2 }}>
              Engagement
            </Typography>
            <Typography>
              Questions: {validation.engagement.question_count}
              <br />
              Quotes: {validation.engagement.quote_count}
              <br />
              Transition Words: {validation.engagement.transition_words}
            </Typography>
          </Paper>
        )}
      </Box>
    </Container>
  );
};

export default ScriptEditor;
