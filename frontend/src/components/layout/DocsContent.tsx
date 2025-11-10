import { Upload, Search, FileJson, GitBranch, BarChart3, Filter } from 'lucide-react';
import { Separator } from '@/components/ui/separator';

export function DocsContent() {
  return (
    <div className="space-y-6 text-sm">
      {/* Introduction */}
      <section>
        <h2 className="text-lg font-semibold mb-3 flex items-center gap-2">
          <FileJson className="h-5 w-5 text-primary" />
          Welcome to Data Dictionary Generator
        </h2>
        <p className="text-muted-foreground leading-relaxed">
          This application helps you manage, explore, and version your data dictionaries.
          Upload JSON files containing field definitions, explore field statistics,
          compare versions, and search across your entire data catalog.
        </p>
      </section>

      <Separator />

      {/* Data Dictionary Management */}
      <section>
        <h3 className="text-base font-semibold mb-2">Data Dictionary Management</h3>
        <p className="text-muted-foreground mb-3">
          View all your data dictionaries on the home page. Each card shows:
        </p>
        <ul className="list-disc list-inside space-y-1 text-muted-foreground ml-2">
          <li><strong>Field count</strong> - Total number of fields in the dictionary</li>
          <li><strong>Version count</strong> - How many versions have been uploaded</li>
          <li><strong>Creation date</strong> - When the dictionary was first created</li>
          <li><strong>Description</strong> - Optional details about the dictionary</li>
        </ul>
        <p className="text-muted-foreground mt-3">
          Click <strong>View Details</strong> to explore fields, view versions, or compare changes.
          Use the delete button to remove dictionaries you no longer need.
        </p>
      </section>

      <Separator />

      {/* Uploading Files */}
      <section>
        <h3 className="text-base font-semibold mb-2 flex items-center gap-2">
          <Upload className="h-4 w-4 text-primary" />
          Uploading Data Dictionaries
        </h3>

        <div className="space-y-3">
          <div>
            <h4 className="font-medium mb-1">Supported File Formats</h4>
            <p className="text-muted-foreground">
              Upload JSON files in the following formats:
            </p>
            <ul className="list-disc list-inside space-y-1 text-muted-foreground ml-2 mt-1">
              <li><code className="bg-muted px-1 py-0.5 rounded">.json</code> - Standard JSON format</li>
              <li><code className="bg-muted px-1 py-0.5 rounded">.jsonl</code> - JSON Lines (one object per line)</li>
              <li><code className="bg-muted px-1 py-0.5 rounded">.ndjson</code> - Newline Delimited JSON</li>
            </ul>
            <p className="text-muted-foreground mt-2">
              Maximum file size: <strong>500MB</strong>
            </p>
          </div>

          <div>
            <h4 className="font-medium mb-1">Required Metadata</h4>
            <ul className="list-disc list-inside space-y-1 text-muted-foreground ml-2">
              <li><strong>Name</strong> - A unique, descriptive name for your dictionary</li>
              <li><strong>Description</strong> (optional) - Additional context about the data</li>
            </ul>
          </div>

          <div>
            <h4 className="font-medium mb-1">AI-Powered Descriptions</h4>
            <p className="text-muted-foreground">
              Enable the <strong>Generate AI Descriptions</strong> option to automatically create
              human-readable descriptions for each field based on its properties. This is especially
              useful for large dictionaries with many technical field names.
            </p>
          </div>

          <div>
            <h4 className="font-medium mb-1">Upload Process</h4>
            <ol className="list-decimal list-inside space-y-1 text-muted-foreground ml-2">
              <li>Drag and drop a file or click to browse</li>
              <li>Fill in the dictionary name and optional description</li>
              <li>Optionally enable AI description generation</li>
              <li>Click <strong>Upload Dictionary</strong></li>
              <li>Monitor progress with the visual progress bar</li>
              <li>You'll be redirected to the dictionary detail page when complete</li>
            </ol>
          </div>
        </div>
      </section>

      <Separator />

      {/* Exploring Fields */}
      <section>
        <h3 className="text-base font-semibold mb-2 flex items-center gap-2">
          <Search className="h-4 w-4 text-primary" />
          Exploring Fields
        </h3>

        <div className="space-y-3">
          <div>
            <h4 className="font-medium mb-1">Field Explorer Table</h4>
            <p className="text-muted-foreground">
              The field explorer provides an interactive table with powerful features:
            </p>
            <ul className="list-disc list-inside space-y-1 text-muted-foreground ml-2 mt-1">
              <li><strong>Sorting</strong> - Click column headers to sort ascending/descending</li>
              <li><strong>Filtering</strong> - Use column-specific filters to narrow results</li>
              <li><strong>Global Search</strong> - Search across all field properties at once</li>
              <li><strong>Pagination</strong> - Navigate through large datasets efficiently</li>
            </ul>
          </div>

          <div>
            <h4 className="font-medium mb-1">Field Information</h4>
            <p className="text-muted-foreground mb-1">Each field displays:</p>
            <ul className="list-disc list-inside space-y-1 text-muted-foreground ml-2">
              <li><strong>Field Name</strong> - The technical name of the field</li>
              <li><strong>Field Path</strong> - Nested path for complex structures (e.g., user.address.city)</li>
              <li><strong>Data Type</strong> - Basic data type (string, number, boolean, etc.)</li>
              <li><strong>Semantic Type</strong> - Business meaning (email, phone, date, etc.)</li>
              <li><strong>PII Status</strong> - Whether the field contains Personally Identifiable Information</li>
            </ul>
          </div>

          <div>
            <h4 className="font-medium mb-1">Field Details</h4>
            <p className="text-muted-foreground">
              Click any field row to open a detailed panel showing:
            </p>
            <ul className="list-disc list-inside space-y-1 text-muted-foreground ml-2 mt-1">
              <li>Complete field metadata and properties</li>
              <li>Statistical analysis and distributions</li>
              <li>Sample values from your data</li>
              <li>Nullability information</li>
              <li>Business annotations (name, tags, owner)</li>
            </ul>
          </div>
        </div>
      </section>

      <Separator />

      {/* Understanding Statistics */}
      <section>
        <h3 className="text-base font-semibold mb-2 flex items-center gap-2">
          <BarChart3 className="h-4 w-4 text-primary" />
          Understanding Field Statistics
        </h3>

        <div className="space-y-3">
          <p className="text-muted-foreground">
            Field statistics help you understand data quality and distributions:
          </p>

          <div>
            <h4 className="font-medium mb-1">Null Percentage</h4>
            <p className="text-muted-foreground">
              A pie chart showing the proportion of null/missing values versus populated values.
              High null percentages may indicate data quality issues or optional fields.
            </p>
          </div>

          <div>
            <h4 className="font-medium mb-1">Numeric Distributions</h4>
            <p className="text-muted-foreground">
              For numeric fields, you'll see:
            </p>
            <ul className="list-disc list-inside space-y-1 text-muted-foreground ml-2 mt-1">
              <li><strong>Histogram</strong> - Distribution of values across ranges</li>
              <li><strong>Box Plot</strong> - Quartiles, median, and outliers visualization</li>
              <li><strong>Min/Max</strong> - Range of values in the dataset</li>
              <li><strong>Mean/Median</strong> - Central tendency measures</li>
            </ul>
          </div>

          <div>
            <h4 className="font-medium mb-1">Sample Values</h4>
            <p className="text-muted-foreground">
              View actual sample values from your data to understand the content and format
              of each field. Particularly useful for categorical fields and text data.
            </p>
          </div>

          <div>
            <h4 className="font-medium mb-1">Data Type Specific Stats</h4>
            <p className="text-muted-foreground">
              Different visualizations appear based on the field's data type. String fields
              show different statistics than numeric fields, and boolean fields show
              true/false distributions.
            </p>
          </div>
        </div>
      </section>

      <Separator />

      {/* Version Management */}
      <section>
        <h3 className="text-base font-semibold mb-2 flex items-center gap-2">
          <GitBranch className="h-4 w-4 text-primary" />
          Version Management & Comparison
        </h3>

        <div className="space-y-3">
          <div>
            <h4 className="font-medium mb-1">Version History</h4>
            <p className="text-muted-foreground">
              Track changes to your data dictionary over time. Each upload creates a new version,
              preserving the complete history. The version timeline shows all versions with
              their creation dates and metadata.
            </p>
          </div>

          <div>
            <h4 className="font-medium mb-1">Comparing Versions</h4>
            <p className="text-muted-foreground mb-1">
              Select two versions to see what changed between them:
            </p>
            <ul className="list-disc list-inside space-y-1 text-muted-foreground ml-2 mt-1">
              <li><strong>Fields Added</strong> - New fields introduced in the later version</li>
              <li><strong>Fields Removed</strong> - Fields that no longer exist</li>
              <li><strong>Fields Modified</strong> - Changes to existing field properties</li>
              <li><strong>Breaking Changes</strong> - Changes that may affect downstream systems</li>
            </ul>
          </div>

          <div>
            <h4 className="font-medium mb-1">Breaking Changes</h4>
            <p className="text-muted-foreground">
              Breaking changes are highlighted and include:
            </p>
            <ul className="list-disc list-inside space-y-1 text-muted-foreground ml-2 mt-1">
              <li>Data type changes (e.g., string → number)</li>
              <li>Required fields becoming optional or vice versa</li>
              <li>Field removals</li>
              <li>Semantic type changes that affect interpretation</li>
            </ul>
            <p className="text-muted-foreground mt-2">
              Review breaking changes carefully before deploying updates to production systems.
            </p>
          </div>

          <div>
            <h4 className="font-medium mb-1">Version Selection</h4>
            <p className="text-muted-foreground">
              Use the version selector dropdown to view fields from a specific version.
              The latest version is shown by default, but you can switch to any historical
              version to see how your data dictionary evolved.
            </p>
          </div>
        </div>
      </section>

      <Separator />

      {/* Search & Filtering */}
      <section>
        <h3 className="text-base font-semibold mb-2 flex items-center gap-2">
          <Filter className="h-4 w-4 text-primary" />
          Global Search & Filtering
        </h3>

        <div className="space-y-3">
          <div>
            <h4 className="font-medium mb-1">Quick Search</h4>
            <p className="text-muted-foreground">
              Use the search bar in the header to quickly find fields across all dictionaries.
              The quick search redirects you to the full search page with your query.
            </p>
          </div>

          <div>
            <h4 className="font-medium mb-1">Advanced Filtering</h4>
            <p className="text-muted-foreground mb-1">
              The global search page offers powerful filters:
            </p>
            <ul className="list-disc list-inside space-y-1 text-muted-foreground ml-2 mt-1">
              <li><strong>Data Type</strong> - Filter by string, number, boolean, etc.</li>
              <li><strong>Semantic Type</strong> - Find email, phone, date fields, etc.</li>
              <li><strong>PII Status</strong> - Filter for fields containing personal information</li>
              <li><strong>Dictionary</strong> - Search within specific dictionaries</li>
            </ul>
          </div>

          <div>
            <h4 className="font-medium mb-1">Search Results</h4>
            <p className="text-muted-foreground">
              Results show matching fields from all dictionaries with key information.
              Click any result to navigate directly to that field's dictionary detail page.
              Results are paginated for easy navigation through large result sets.
            </p>
          </div>

          <div>
            <h4 className="font-medium mb-1">Debounced Search</h4>
            <p className="text-muted-foreground">
              Search queries are automatically debounced to reduce server load and provide
              a smooth user experience. Results update shortly after you stop typing.
            </p>
          </div>
        </div>
      </section>

      <Separator />

      {/* Export */}
      <section>
        <h3 className="text-base font-semibold mb-2">Exporting to Excel</h3>
        <p className="text-muted-foreground">
          Export any dictionary to Excel format for offline analysis or sharing with
          stakeholders. The export includes all field information, statistics, and
          metadata in a well-formatted spreadsheet.
        </p>
        <p className="text-muted-foreground mt-2">
          Click the <strong>Export to Excel</strong> button on the dictionary detail page
          to download a comprehensive Excel file.
        </p>
      </section>

      <Separator />

      {/* Tips */}
      <section>
        <h3 className="text-base font-semibold mb-2">Tips & Best Practices</h3>
        <ul className="list-disc list-inside space-y-2 text-muted-foreground ml-2">
          <li>
            <strong>Organize dictionaries</strong> - Use clear, consistent naming conventions
            for your dictionaries to make them easy to find
          </li>
          <li>
            <strong>Version regularly</strong> - Upload new versions as your schema evolves
            to maintain a complete history
          </li>
          <li>
            <strong>Review breaking changes</strong> - Always check version comparisons before
            deploying schema changes
          </li>
          <li>
            <strong>Use descriptions</strong> - Add descriptions to dictionaries to provide
            context for team members
          </li>
          <li>
            <strong>Monitor PII fields</strong> - Regularly review fields marked as PII to
            ensure compliance with data privacy regulations
          </li>
          <li>
            <strong>Export for documentation</strong> - Use Excel exports to share data
            dictionary documentation with non-technical stakeholders
          </li>
        </ul>
      </section>
    </div>
  );
}
