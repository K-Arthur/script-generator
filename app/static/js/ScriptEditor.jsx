import React, { useState, useEffect, useRef } from 'react';
import {
  Box,
  Button,
  Container,
  TextField,
  Typography,
  LinearProgress,
  Paper,
  Grid,
  Alert,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  Tooltip,
  IconButton,
  Menu,
} from '@mui/material';
import {
  FileUpload as FileUploadIcon,
  Download as DownloadIcon,
  Info as InfoIcon,
} from '@mui/icons-material';

const ScriptEditor = () => {
  const [content, setContent] = useState('');
  const [highlightedConcept, setHighlightedConcept] = useState('');
  const [previousTopic, setPreviousTopic] = useState('');
  const [script, setScript] = useState('');
  const [validation, setValidation] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [templates, setTemplates] = useState([]);
  const [selectedTemplate, setSelectedTemplate] = useState('');
  const [exportAnchorEl, setExportAnchorEl] = useState(null);
  const pollInterval = useRef(null);

  useEffect(() => {
    // Fetch available templates
    fetch('/api/templates')
      .then((response) => response.json())
      .then((data) => {
        if (data.status === 'success') {
          setTemplates(Object.entries(data.templates));
        }
      })
      .catch((err) => {
        console.error('Error fetching templates:', err);
      });
  }, []);

  const handleFileUpload = async (event) => {
    const file = event.target.files[0];
    if (!file) return;

    const formData = new FormData();
    formData.append('file', file);

    try {
      const response = await fetch('/api/upload-file', {
        method: 'POST',
        body: formData,
      });

      const data = await response.json();
      if (data.status === 'success') {
        setContent(data.content);
      } else {
        setError('Error uploading file');
      }
    } catch (err) {
      setError('Error uploading file: ' + err.message);
    }
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
          template_name: selectedTemplate,
          highlighted_concept: highlightedConcept,
          previous_topic: previousTopic,
        }),
      });

      const data = await response.json();
      if (data.task_id) {
        pollInterval.current = setInterval(
          () => checkScriptStatus(data.task_id),
          2000
        );
      } else {
        setError('Error generating script');
        setLoading(false);
      }
    } catch (err) {
      setError('Error generating script: ' + err.message);
      setLoading(false);
    }
  };

  const checkScriptStatus = async (taskId) => {
    try {
      const response = await fetch(`/api/script-status/${taskId}`);
      const data = await response.json();

      if (data.status === 'completed') {
        clearInterval(pollInterval.current);
        setScript(data.script);
        setValidation(data.validation);
        setLoading(false);
      } else if (data.status === 'failed') {
        clearInterval(pollInterval.current);
        setError(data.error);
        setLoading(false);
      }
    } catch (err) {
      clearInterval(pollInterval.current);
      setError('Error checking script status: ' + err.message);
      setLoading(false);
    }
  };

  const validateScript = async () => {
    try {
      const response = await fetch('/api/validate-script', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          script,
          template_name: selectedTemplate,
        }),
      });

      const data = await response.json();
      if (data.status === 'success') {
        setValidation(data.validation);
      }
    } catch (err) {
      setError('Error validating script: ' + err.message);
    }
  };

  const handleExportClick = (event) => {
    setExportAnchorEl(event.currentTarget);
  };

  const handleExportClose = () => {
    setExportAnchorEl(null);
  };

  const handleExport = async (format) => {
    try {
      const response = await fetch('/api/export-script', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          script,
          format,
        }),
      });

      if (response.ok) {
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `script.${format}`;
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
        document.body.removeChild(a);
      } else {
        setError('Error exporting script');
      }
    } catch (err) {
      setError('Error exporting script: ' + err.message);
    }
    handleExportClose();
  };

  useEffect(() => {
    return () => {
      if (pollInterval.current) {
        clearInterval(pollInterval.current);
      }
    };
  }, []);

  return (
    <Container maxWidth="lg">
      <Box sx={{ my: 4 }}>
        <Typography variant="h4" component="h1" gutterBottom>
          Script Generator
        </Typography>

        {error && (
          <Alert severity="error" sx={{ mb: 2 }}>
            {error}
          </Alert>
        )}

        <Grid container spacing={3}>
          <Grid item xs={12} md={6}>
            <Paper sx={{ p: 2 }}>
              <Typography variant="h6" gutterBottom>
                Input
              </Typography>

              <Button
                variant="contained"
                component="label"
                startIcon={<FileUploadIcon />}
                sx={{ mb: 2 }}
              >
                Upload File
                <input
                  type="file"
                  hidden
                  onChange={handleFileUpload}
                  accept=".txt,.doc,.docx"
                />
              </Button>

              <FormControl fullWidth sx={{ mb: 2 }}>
                <InputLabel>Template</InputLabel>
                <Select
                  value={selectedTemplate}
                  onChange={(e) => setSelectedTemplate(e.target.value)}
                  label="Template"
                >
                  <MenuItem value="">
                    <em>None</em>
                  </MenuItem>
                  {templates.map(([key, template]) => (
                    <MenuItem key={key} value={key}>
                      {template.name}
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>

              <TextField
                fullWidth
                multiline
                rows={10}
                value={content}
                onChange={(e) => setContent(e.target.value)}
                placeholder="Enter your content here..."
                sx={{ mb: 2 }}
              />

              <TextField
                fullWidth
                value={highlightedConcept}
                onChange={(e) => setHighlightedConcept(e.target.value)}
                label="Highlighted Concept"
                sx={{ mb: 2 }}
              />

              <TextField
                fullWidth
                value={previousTopic}
                onChange={(e) => setPreviousTopic(e.target.value)}
                label="Previous Topic"
                sx={{ mb: 2 }}
              />

              <Button
                variant="contained"
                onClick={generateScript}
                disabled={loading || !content}
                fullWidth
              >
                Generate Script
              </Button>
            </Paper>
          </Grid>

          <Grid item xs={12} md={6}>
            <Paper sx={{ p: 2 }}>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 2 }}>
                <Typography variant="h6">Generated Script</Typography>
                {script && (
                  <Box>
                    <IconButton onClick={handleExportClick}>
                      <DownloadIcon />
                    </IconButton>
                    <Menu
                      anchorEl={exportAnchorEl}
                      open={Boolean(exportAnchorEl)}
                      onClose={handleExportClose}
                    >
                      <MenuItem onClick={() => handleExport('txt')}>
                        Export as TXT
                      </MenuItem>
                      <MenuItem onClick={() => handleExport('html')}>
                        Export as HTML
                      </MenuItem>
                      <MenuItem onClick={() => handleExport('md')}>
                        Export as Markdown
                      </MenuItem>
                    </Menu>
                  </Box>
                )}
              </Box>

              {loading && <LinearProgress sx={{ mb: 2 }} />}

              <TextField
                fullWidth
                multiline
                rows={15}
                value={script}
                onChange={(e) => setScript(e.target.value)}
                sx={{ mb: 2 }}
              />

              <Button
                variant="outlined"
                onClick={validateScript}
                disabled={!script}
                fullWidth
                sx={{ mb: 2 }}
              >
                Validate Script
              </Button>

              {validation && (
                <Box>
                  <Typography variant="h6" gutterBottom>
                    Validation Results
                  </Typography>

                  <Box sx={{ mb: 2 }}>
                    <Typography variant="subtitle1" gutterBottom>
                      Readability Metrics
                    </Typography>
                    <Grid container spacing={2}>
                      <Grid item xs={12} sm={4}>
                        <Tooltip title="Higher score means easier to read (0-100)">
                          <Box>
                            <Typography variant="body2">
                              Flesch Score: {validation.readability.flesch_score.toFixed(1)}
                              <IconButton size="small">
                                <InfoIcon fontSize="small" />
                              </IconButton>
                            </Typography>
                          </Box>
                        </Tooltip>
                      </Grid>
                      <Grid item xs={12} sm={4}>
                        <Typography variant="body2">
                          Grade Level: {validation.readability.grade_level.toFixed(1)}
                        </Typography>
                      </Grid>
                      <Grid item xs={12} sm={4}>
                        <Typography variant="body2">
                          Reading Time: {validation.readability.reading_time.toFixed(1)} min
                        </Typography>
                      </Grid>
                    </Grid>
                  </Box>

                  <Box sx={{ mb: 2 }}>
                    <Typography variant="subtitle1" gutterBottom>
                      Structure Analysis
                    </Typography>
                    <Grid container spacing={2}>
                      <Grid item xs={12} sm={4}>
                        <Typography variant="body2">
                          Words: {validation.structure.word_count}
                        </Typography>
                      </Grid>
                      <Grid item xs={12} sm={4}>
                        <Typography variant="body2">
                          Sentences: {validation.structure.sentence_count}
                        </Typography>
                      </Grid>
                      <Grid item xs={12} sm={4}>
                        <Typography variant="body2">
                          Paragraphs: {validation.structure.paragraph_count}
                        </Typography>
                      </Grid>
                    </Grid>
                  </Box>

                  <Box sx={{ mb: 2 }}>
                    <Typography variant="subtitle1" gutterBottom>
                      Engagement Metrics
                    </Typography>
                    <Grid container spacing={2}>
                      <Grid item xs={12} sm={4}>
                        <Typography variant="body2">
                          Questions: {validation.engagement.question_count}
                        </Typography>
                      </Grid>
                      <Grid item xs={12} sm={4}>
                        <Typography variant="body2">
                          Quotes: {validation.engagement.quote_count}
                        </Typography>
                      </Grid>
                      <Grid item xs={12} sm={4}>
                        <Typography variant="body2">
                          Transitions: {validation.engagement.transition_words}
                        </Typography>
                      </Grid>
                    </Grid>
                  </Box>

                  {validation.template_compliance && (
                    <Box>
                      <Typography variant="subtitle1" gutterBottom>
                        Template Compliance
                      </Typography>
                      {Object.entries(validation.template_compliance).map(
                        ([section, details]) => (
                          <Box key={section} sx={{ mb: 1 }}>
                            <Typography variant="body2">
                              {section}:{' '}
                              {details.present ? (
                                details.length_in_range ? (
                                  '✅'
                                ) : (
                                  `⚠️ (${details.actual_length} words, expected ${details.expected_range[0]}-${details.expected_range[1]})`
                                )
                              ) : (
                                '❌ Missing'
                              )}
                            </Typography>
                          </Box>
                        )
                      )}
                    </Box>
                  )}
                </Box>
              )}
            </Paper>
          </Grid>
        </Grid>
      </Box>
    </Container>
  );
};

export default ScriptEditor;
